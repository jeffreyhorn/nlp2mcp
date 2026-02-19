# Sprint 20 Prep Task Prompts

**Purpose:** Ready-to-use prompts for executing each Sprint 20 prep task (Tasks 2–10).
Each prompt is self-contained: it includes the full task context, known unknowns to verify,
PREP_PLAN.md update instructions, CHANGELOG.md update instructions, quality gate, commit
message format, and PR instructions.

**Reference documents:**
- `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` — task definitions
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` — unknowns to verify
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — lexer subcategory taxonomy
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` — IndexOffset design
- `docs/issues/ISSUE_753_circle-mcp-locally-infeasible.md` — .l init gap (circle)
- `docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md` — .l init gap (bearing)
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` — accounting vars
- `docs/issues/ISSUE_763_chenery-mcp-division-by-zero-del-parameter.md` — AD condition

---

## Task 2 Prompt: Audit IndexOffset End-to-End Pipeline State

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 2: Audit
IndexOffset End-to-End Pipeline State.

## Branch
Work on branch `planning/sprint20-task2`. Create it from the current branch
`main`:
  git checkout main 
  git checkout -b planning/sprint20-task2

## Objective
Determine the exact current state of IndexOffset support across all pipeline stages
(parse → IR → AD → emit) and identify the precise remaining gaps for each of the 8
blocked models. Produce a revised effort estimate for the Sprint 20 IndexOffset workstream.

## Background
Sprint 19 IndexOffset progress:
- IR node: Existed since Sprint 9 Day 3 (src/ir/ast.py)
- Grammar/parser: `offset_paren`, `offset_func` rules added in PR #785
- AD integration: `_substitute_index()` + `_apply_index_substitution()` for VarRef/ParamRef/
  DollarConditional (PR #779); `offset_paren`/`offset_func` callback pattern (PR #785)
- Emit layer: `_format_mixed_indices()` already handles IndexOffset (pre-Sprint 19)
- 8 blocked models: Per `INDEX_OFFSET_DESIGN_OPTIONS.md`: `launch`, `mine`, `sparta`,
  `tabora`, `ampl`, `otpop`, `robert`, `pak` (with `launch`/`mine`/`sparta`/`tabora` as
  Subcategory D lead/lag models; `ampl`/`otpop` as cascading translate failures; `robert`
  as path_syntax_error; `pak` as path_solve_terminated)

Reference: docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md
Original effort estimate: ~4h remaining (AD work done in Sprint 19).

## What Needs to Be Done

1. Run each of the 8 blocked models through the full pipeline:
   ```
   python -m src.cli data/gamslib/raw/launch.gms
   python -m src.cli data/gamslib/raw/mine.gms
   python -m src.cli data/gamslib/raw/sparta.gms
   python -m src.cli data/gamslib/raw/tabora.gms
   python -m src.cli data/gamslib/raw/ampl.gms
   python -m src.cli data/gamslib/raw/otpop.gms
   python -m src.cli data/gamslib/raw/robert.gms
   python -m src.cli data/gamslib/raw/pak.gms
   ```

2. For each model, classify current failure stage:
   - parse (lexer_invalid_char or parse error)
   - translate (internal_error at translate stage)
   - solve (PATH infeasibility)
   - none (already works end-to-end)

3. Check the Sprint 19 xfail test:
   - Find it: grep -rn "xfail\|sum.*collapse.*IndexOffset\|IndexOffset.*wrt" tests/
   - Run: python -m pytest tests/ -k "IndexOffset" -v
   - Determine: is the xfail case a real blocker for any of the 8 models, or a cleanup item?

4. Check the emit layer for circular lead/lag (++ / --):
   - grep -n "circular\|\+\+\|--\|format_mixed\|IndexOffset" src/emit/expr_to_gams.py
   - Determine: does _format_mixed_indices() handle circular offset, or only linear?

5. Produce a revised effort estimate based on actual findings.

6. Document findings in `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md` with:
   - Per-model status table: | Model | Current Stage | Error/Token | Remaining Work | Est. Hours |
   - Revised total effort estimate for Sprint 20 IndexOffset workstream
   - xfail test assessment (cleanup vs. critical path)
   - Emit layer circular lead/lag assessment

## Known Unknowns to Verify
After completing the audit, update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`
for these unknowns. Change each status from `🔍 Status: INCOMPLETE` to
`✅ Status: VERIFIED` (or `❌ Status: WRONG — [correction]`). Add a Findings section
below each Verification Results heading with evidence and decisions.

### Unknown 6.1: Current pipeline failure stage for each of the 8 IndexOffset-blocked models
Update with: actual status of each model, whether they moved past parse, what errors remain.

### Unknown 6.2: Does the xfail test represent a real blocker for any model?
Update with: what the xfail tests, whether any of the 8 models trigger that case, recommended fix priority.

### Unknown 6.3: Does the emit layer correctly handle circular lead/lag (++/--)?
Update with: what _format_mixed_indices() actually handles, whether any of the 8 models need circular offset.

## PREP_PLAN.md Updates
After completing the task, update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 2:
1. Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
2. Fill in the `### Changes` section with a bullet list of files created/modified
3. Fill in the `### Result` section with a 1–3 sentence summary of findings and the
   revised effort estimate
4. Check off all acceptance criteria: change `- [ ]` → `- [x]`

## CHANGELOG.md Update
Add a new entry at the top of the `## [Unreleased]` section in CHANGELOG.md:

```
### Sprint 20 Prep Task 2: Audit IndexOffset End-to-End Pipeline State - <DATE>

**Branch:** `planning/sprint20-task2`

#### Summary
<2–4 sentence summary of findings: model statuses, revised effort estimate, key discoveries>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 6.1, 6.2, 6.3 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 2 → COMPLETE
```

## Quality Gate
This task is documentation/research only — no Python source files should be modified.
If you do modify any Python files, run the full quality gate before committing:
  make typecheck && make lint && make format && make test

For documentation-only commits, verify the docs were created:
  ls docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md
  grep -c "| " docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 2: Audit IndexOffset pipeline state

- Create INDEXOFFSET_AUDIT.md: per-model status for 8 blocked models
- Revised IndexOffset effort estimate: Xh (was ~4h)
- Verify KNOWN_UNKNOWNS 6.1, 6.2, 6.3
- Update PREP_PLAN.md Task 2 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
After committing and pushing, create a PR:
  git push origin planning/sprint20-task2
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 2: Audit IndexOffset End-to-End Pipeline State" \
    --body "## Summary
Completes Sprint 20 Prep Task 2 from PREP_PLAN.md.

## Deliverables
- [ ] INDEXOFFSET_AUDIT.md — per-model status table for all 8 blocked models
- [ ] Revised effort estimate for Sprint 20 IndexOffset workstream
- [ ] KNOWN_UNKNOWNS.md — Unknowns 6.1, 6.2, 6.3 verified
- [ ] PREP_PLAN.md Task 2 → COMPLETE

## Key Findings
<!-- Fill in after completing the task -->

## Unknowns Verified
- 6.1: Current failure stage for each of the 8 IndexOffset-blocked models
- 6.2: xfail test (sum-collapse-with-IndexOffset-wrt) scope
- 6.3: Emit layer circular lead/lag support"

Then wait for reviewer comments. Address any comments raised by the reviewer before
merging. Reply directly to each review comment explaining what you changed or why
you disagree.
```

---

## Task 3 Prompt: Catalog Remaining lexer_invalid_char Subcategories

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 3: Catalog
Remaining lexer_invalid_char Subcategories.

## Branch
Work on branch `planning/sprint20-task3`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task3

## Objective
Run all remaining `lexer_invalid_char` models (27 after Sprint 19) through the parser
with verbose output, verify their subcategory classification, and identify which models
have moved between categories or been resolved since the Sprint 19 LEXER_ERROR_CATALOG
was written. Identify the top-ROI subcategories and quick wins for Sprint 20.

## Background
From LEXER_ERROR_CATALOG.md Sprint 19 baseline (72 models):
- Sprint 19 resolved ~45 models (72 → 27 remaining)
- Reference taxonomy: docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md
- Remaining subcategories (estimates — verify actuals):
  - C (Put Statement Format): ~3–4 remain
  - D (Lead/Lag): ~2 remain (ampl/otpop may now parse after Sprint 19 PRs)
  - E (Special Values): ~3–5 remain
  - G (Set Element Descriptions): ~4 remain
  - H (Control Flow): ~2 remain
  - J (Bracket/Brace): ~3 remain
  - K (Miscellaneous): ~7 remain

First read docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md to understand
the full A–K taxonomy and get the exact model list for each subcategory.

## What Needs to Be Done

1. Get the current list of lexer_invalid_char models:
   .venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet 2>&1 | grep lexer_invalid_char
   (Or read data/gamslib/gamslib_status.json for current status of all models.)

2. For each of the failing models, run the parser with enough verbosity to capture
   the specific failing token and line number:
   python -m src.cli data/gamslib/raw/<model>.gms 2>&1 | head -30

3. Re-classify each model into the existing A–K taxonomy based on the failing token.
   If the pattern doesn't fit any existing subcategory, define a new one.

4. Note any models that no longer fail (silent fixes from Sprint 19). Confirm: do
   the 27 remaining models exactly match the pre-Sprint-19 residual predictions, or
   have some been silently fixed?

5. Rank subcategories by model count (highest ROI first).

6. For each subcategory, estimate fix effort:
   - Quick win: ≤2h grammar change, ≥2 models unblocked
   - Medium: 2–4h
   - Complex: >4h or requires preprocessor/IR changes

7. Identify the top 3 highest-ROI subcategories and at least 2 quick wins.

8. Create `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` with:
   - Per-model table: | Model | Subcategory | Failing Token/Line | Fix Effort |
   - Per-subcategory summary: | Subcategory | Name | Count | Fix Effort | Notes |
   - Top-3 highest-ROI list with effort estimates
   - Quick wins section

## Known Unknowns to Verify
After completing the catalog, update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 4.1: Exact subcategories of the 27 remaining lexer_invalid_char models
Update with: actual subcategory distribution (counts per subcategory), whether dominant
subcategories match the assumption (G, H, J, K), and which has highest ROI.

### Unknown 4.2: Any lexer_invalid_char models already fixed by Sprint 19 but not re-run?
Update with: actual count after re-run (is it still 27, or fewer?), any silent fixes found.

### Unknown 4.3: Are Subcategory G (set element descriptions) fixes straightforward?
Update with: exact failing token in Subcategory G models, whether it's grammar-only,
interactions with existing rules, revised effort estimate.

### Unknown 4.4: Do lead/lag (Subcategory D) lexer failures resolve via IndexOffset work?
Update with: which models remain in Subcategory D after Sprint 19, whether their failing
tokens are covered by offset_paren/offset_func rules, whether they need separate grammar work.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 3:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created/modified
3. Fill in `### Result` with actual subcategory counts, top-ROI findings, and quick wins
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 3: Catalog Remaining lexer_invalid_char Subcategories - <DATE>

**Branch:** `planning/sprint20-task3`

#### Summary
<2–4 sentences: actual 27-model subcategory distribution, top ROI subcategories, quick wins identified>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 4.1, 4.2, 4.3, 4.4 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 3 → COMPLETE
```

## Quality Gate
Documentation-only task. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md
  grep -c "^|" docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md

If any Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 3: Catalog lexer_invalid_char subcategories

- Create LEXER_ERROR_CATALOG_UPDATE.md: 27 models reclassified into subcategories
- Top ROI subcategories: <list>
- Quick wins identified: <count>
- Verify KNOWN_UNKNOWNS 4.1, 4.2, 4.3, 4.4
- Update PREP_PLAN.md Task 3 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task3
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 3: Catalog Remaining lexer_invalid_char Subcategories" \
    --body "## Summary
Completes Sprint 20 Prep Task 3 from PREP_PLAN.md.

## Deliverables
- [ ] LEXER_ERROR_CATALOG_UPDATE.md — 27 models with subcategory, token, fix estimate
- [ ] Prioritized subcategory list (top 3 by ROI)
- [ ] At least 2 quick wins identified
- [ ] KNOWN_UNKNOWNS.md — Unknowns 4.1, 4.2, 4.3, 4.4 verified
- [ ] PREP_PLAN.md Task 3 → COMPLETE

## Key Findings
<!-- Fill in: actual subcategory distribution, top ROI, quick wins -->

## Unknowns Verified
- 4.1: Actual subcategory distribution of 27 remaining models
- 4.2: Whether any models silently fixed by Sprint 19
- 4.3: Subcategory G fix complexity
- 4.4: Subcategory D / IndexOffset overlap"

Then wait for reviewer comments and address them before merging.
```

---

## Task 4 Prompt: Investigate .l Initialization Emission Gap

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 4: Investigate
.l Initialization Emission Gap.

## Branch
Work on branch `planning/sprint20-task4`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task4

## Objective
Determine exactly what changes are needed to emit `.l` variable level initialization
statements from the IR in the MCP prolog. Confirm whether this fix resolves PATH
infeasibility for circle (#753) and bearing (#757). Produce a revised effort estimate
and a concrete design document.

## Background
- docs/issues/ISSUE_753_circle-mcp-locally-infeasible.md — circle uses .l assignments;
  MCP omits them; PATH fails with locally infeasible without good starting point.
  Sprint 19 PR #750 fixed determinism (execseed); remaining issue is initialization.
- docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md — bearing uses .l and .scale;
  .l emission may partially help; .scale is a separate (harder) gap.
- src/ir/parser.py — IR parser; question: does it capture .l attribute assignments?
- src/ir/ast.py — IR AST node types
- src/emit/emit_gams.py (or model.py) — MCP emitter; question: where would .l assignments go?

## What Needs to Be Done

1. Check whether .l assignments are captured in the current IR:
   python -c "
   import sys; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   ir = parse_file('data/gamslib/raw/circle.gms')
   # Inspect all assignment-like objects in the IR
   for attr in dir(ir):
       val = getattr(ir, attr)
       if isinstance(val, list) and val:
           print(attr, type(val[0]))
   "
   Also: grep -n '\.l\|var_attr\|attr_assign\|level\|AttrAssign' src/ir/parser.py src/ir/ast.py | head -30

2. Check the MCP emitter structure to understand where .l assignments would go:
   grep -n "def emit\|prolog\|Model\|Solve\|assignment\|init" src/emit/emit_gams.py | head -30
   View a generated MCP file: head -80 data/gamslib/mcp/circle_mcp.gms

3. Check how many models in the corpus have .l assignments:
   grep -rl "\.l(" data/gamslib/raw/ | wc -l
   grep -rl "\.l(" data/gamslib/raw/ | xargs -I{} basename {} .gms

4. For bearing specifically, check whether .scale is also present:
   grep "\.scale\|\.l(" data/gamslib/raw/bearing.gms | head -10

5. Determine the fix strategy:
   - If .l IS captured in the IR: the fix is in the emit layer only (~1–2h)
   - If .l is NOT captured: fix requires IR parser changes + emit layer changes (~3–5h)
   - Document before/after example: what the emitted MCP should look like with .l init

6. Create `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md` with:
   - Finding: Is .l captured in IR? (yes/no, evidence)
   - Fix location: file(s) and approximate line range(s)
   - Fix strategy: code sketch of the change
   - Before/after example using circle.gms
   - Bearing assessment: same fix applies / .scale is primary blocker / both needed
   - Revised effort estimate: ±1h precision
   - Expected impact: which models benefit, predicted solve rate improvement

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 1.1: Does the IR currently capture .l variable level assignments?
Update with: yes/no finding, which AST node type (if any), evidence from grep/inspection.

### Unknown 1.2: Will .l initialization alone resolve PATH infeasibility for circle and bearing?
Update with: whether circle.gms has useful .l assignments, whether bearing needs .scale too,
confidence level that the fix will deliver PATH convergence.

### Unknown 1.3: Does the MCP emit pipeline have a defined prolog section?
Update with: what the emitter structure actually looks like, where pre-solve assignments
would go, whether a prolog concept exists or needs to be created.

### Unknown 1.4: Are there models beyond circle and bearing that would benefit?
Update with: actual count of models with .l assignments in the corpus.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 4:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created/modified
3. Fill in `### Result` with the key finding (IR captures .l or not), fix location,
   and revised effort estimate
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 4: Investigate .l Initialization Emission Gap - <DATE>

**Branch:** `planning/sprint20-task4`

#### Summary
<2–4 sentences: whether IR captures .l, fix location, bearing vs circle scope, revised estimate>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 1.1, 1.2, 1.3, 1.4 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 4 → COMPLETE
```

## Quality Gate
Documentation/research only — no Python source changes expected.
Verify:
  ls docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md
  grep "Fix Location" docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md

If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 4: Investigate .l emission gap

- Create L_INIT_EMISSION_DESIGN.md: .l IR capture finding + fix strategy
- IR captures .l: <yes/no>; fix location: <file>
- Verify KNOWN_UNKNOWNS 1.1, 1.2, 1.3, 1.4
- Update PREP_PLAN.md Task 4 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task4
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 4: Investigate .l Initialization Emission Gap" \
    --body "## Summary
Completes Sprint 20 Prep Task 4 from PREP_PLAN.md.

## Deliverables
- [ ] L_INIT_EMISSION_DESIGN.md — design document for .l emission fix
- [ ] Revised effort estimate for Sprint 20 Priority 1 (.l emission)
- [ ] KNOWN_UNKNOWNS.md — Unknowns 1.1, 1.2, 1.3, 1.4 verified
- [ ] PREP_PLAN.md Task 4 → COMPLETE

## Key Findings
<!-- Fill in: IR captures .l or not, fix location, bearing/circle scope, revised estimate -->

## Unknowns Verified
- 1.1: Whether IR currently captures .l assignments
- 1.2: Whether .l init alone resolves circle/bearing PATH infeasibility
- 1.3: Whether MCP emitter has a prolog section
- 1.4: Count of corpus models with .l assignments"

Then wait for reviewer comments and address them before merging.
```

---

## Task 5 Prompt: Audit Translate internal_error Models

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 5: Audit
Translate internal_error Models.

## Branch
Work on branch `planning/sprint20-task5`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task5

## Objective
Identify the current set of models failing with `internal_error` at the translate stage,
classify each by root cause, and determine which are addressable in Sprint 20 vs. require
architectural changes. Also determine the current count of `model_no_objective_def` failures
(Unknown 8.1).

## Background
PROJECT_PLAN.md Sprint 20 allocates 6–8h to "Translation Internal Error Fixes (~5 models)."
Sprint 19 reduced parse-stage internal errors but the translate-stage population needs a fresh
audit. Models newly parsing after Sprint 19's 46-model improvement will enter translate for the
first time — some may have new translate internal errors.

Root cause categories for translate errors:
- Missing AD rule (no derivative for a specific function in a specific context)
- IR construction crash (unexpected AST node type in KKT assembly)
- KKT assembly error (domain mismatch, unsupported expression)
- IndexOffset-related (would be fixed by the IndexOffset workstream)

## What Needs to Be Done

1. Get the current count and list of translate-stage failures:
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | grep internal_error
   (Or read data/gamslib/gamslib_status.json for all model statuses.)

2. For each translate-stage internal_error model, run with full stack trace:
   python -m src.cli data/gamslib/raw/<model>.gms 2>&1

3. Classify each failure by root cause (see categories above). Note:
   - Which exception type? (KeyError, AttributeError, NotImplementedError, etc.)
   - Which function? (grep the traceback)
   - Is it IndexOffset-related?

4. Identify: do any failures share the same exception + call stack? (systematic fix opportunity)

5. Get the current count and patterns of `model_no_objective_def` failures:
   python -c "
   import json
   with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
   no_obj = []
   for m in data.get('models', []):
       translate_stage = m.get('nlp2mcp_translate', {})
       if translate_stage.get('status') == 'failure' and \
          (translate_stage.get('error') or {}).get('category') == 'model_no_objective_def':
           no_obj.append(m)
   print('Count:', len(no_obj))
   for m in no_obj: print(m.get('model_name'), m.get('nlp2mcp_translate'))
   "

6. Create `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md` with:
   - Per-model table: | Model | Exception Type | Function | Root Cause Category | Fixable in S20? |
   - Systematic fix opportunities (shared root causes)
   - IndexOffset-related vs. non-IndexOffset breakdown
   - model_no_objective_def: count, patterns, and whether patterns suggest a common fix
   - Recommended Sprint 20 target count (PROJECT_PLAN.md says 5 — verify or correct)

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 7.1: How many models currently fail with internal_error at translate stage?
Update with: actual current count, root cause breakdown, count addressable in Sprint 20.

### Unknown 7.2: Are any translate internal errors caused by the same root cause?
Update with: whether shared root causes exist, which function/exception, how many models
would be fixed by a single change.

### Unknown 8.1: How many model_no_objective_def models exist and what patterns do they use?
Update with: actual count, the patterns identified, whether PROJECT_PLAN.md's "5 models" is accurate.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 5:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created/modified
3. Fill in `### Result` with actual translate error count, root cause breakdown, and
   model_no_objective_def count
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 5: Audit Translate internal_error Models - <DATE>

**Branch:** `planning/sprint20-task5`

#### Summary
<2–4 sentences: actual translate internal_error count, root cause breakdown, S20-addressable count, no_objective_def count>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 7.1, 7.2, 8.1 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 5 → COMPLETE
```

## Quality Gate
Documentation/research only. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md
  grep -c "^|" docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md

If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 5: Audit translate internal_error models

- Create TRANSLATE_ERROR_AUDIT.md: N models classified by root cause
- S20-addressable: X; deferred: Y; IndexOffset-related: Z
- model_no_objective_def: N models, <pattern summary>
- Verify KNOWN_UNKNOWNS 7.1, 7.2, 8.1
- Update PREP_PLAN.md Task 5 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task5
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 5: Audit Translate internal_error Models" \
    --body "## Summary
Completes Sprint 20 Prep Task 5 from PREP_PLAN.md.

## Deliverables
- [ ] TRANSLATE_ERROR_AUDIT.md — per-model root cause table for translate failures
- [ ] Count of Sprint-20-addressable vs. deferred models
- [ ] model_no_objective_def count and pattern analysis
- [ ] KNOWN_UNKNOWNS.md — Unknowns 7.1, 7.2, 8.1 verified
- [ ] PREP_PLAN.md Task 5 → COMPLETE

## Key Findings
<!-- Fill in: actual counts, root cause breakdown, systematic fix opportunities -->

## Unknowns Verified
- 7.1: Current translate internal_error count and root causes
- 7.2: Systematic vs. case-by-case fix potential
- 8.1: model_no_objective_def count and patterns"

Then wait for reviewer comments and address them before merging.
```

---

## Task 6 Prompt: Investigate Full Pipeline Match Divergence

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 6: Investigate
Full Pipeline Match Divergence.

## Branch
Work on branch `planning/sprint20-task6`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task6

## Objective
Determine why 16 models solve successfully (PATH model status 1) but fail the full pipeline
match check (objective value differs from reference NLP solution). Classify each divergence
by cause. Predict how many would be resolved by the .l initialization emission fix.

## Background
Sprint 19 final state:
- 25 models solve (PATH model status 1)
- 9 full pipeline matches: ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport
- Gap: 16 models solve but don't match

Likely causes:
1. Missing .l initialization — PATH finds a different local optimum
2. Missing .scale scaling — poorly scaled variables cause numerical issues
3. Multiple optima — mathematically correct but different optimum found
4. Tolerance too tight — within acceptable tolerance under different policy
5. KKT formulation error — model solves but MCP is subtly wrong

## What Needs to Be Done

1. Identify the 16 non-matching models. Read data/gamslib/gamslib_status.json to find
   models with solve success but no pipeline match. (Inspect the JSON structure first to
   understand the field names for solve status and match status.)

2. For each of the 16 models:
   a. Compute the objective value gap: |mcp_obj - nlp_obj| / max(1, |nlp_obj|)
   b. Check if the model has .l assignments in the raw GAMS source:
      grep "\.l(" data/gamslib/raw/<model>.gms | wc -l
   c. Check if the model uses .scale:
      grep "\.scale(" data/gamslib/raw/<model>.gms | wc -l
   d. Classify divergence type based on gap size and .l/.scale presence

3. Check the current solution comparison tolerance:
   grep -n "tolerance\|tol\|atol\|rtol\|match\|compare" src/validation/ -r | head -20
   Determine: what tolerance is used? Are any non-matching models within 5% of reference?

4. Verify that all 9 matching models are covered by golden-file tests:
   grep -r "ajax\|blend\|demo1\|himmel11\|house\|mathopt2\|prodmix\|rbrock\|trnsport" \
     tests/ | grep "golden\|fixture\|parametrize" | head -20

5. Create `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` with:
   - Per-model table: | Model | Obj Gap % | Has .l | Has .scale | Divergence Type | Likely Cause |
   - Predicted match count after .l emission fix (count of "initialization" category)
   - Tolerance analysis: any models within 5% that could match with looser tolerance?
   - KKT review candidates: models with >100% gap
   - Golden-file test coverage status for the 9 currently matching models

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 5.1: What is the primary cause of the 16-model solve-success / pipeline-match gap?
Update with: actual distribution of divergence types across the 16 models, whether initialization
is dominant, confidence in the .l emission fix delivering matches.

### Unknown 5.2: Is the solution comparison tolerance calibrated correctly?
Update with: actual tolerance value(s) used, whether any non-matching models are within 5%.

### Unknown 5.3: Do any of the 16 non-matching models have .scale issues?
Update with: count of models using .scale, whether .scale is a primary or secondary blocker.

### Unknown 5.4: Are the 9 currently-matching models at risk of regression?
Update with: whether all 9 are in the golden-file test suite, and whether any of the 9 use
patterns targeted by Sprint 20 workstreams (IndexOffset, accounting vars, AD condition).

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 6:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created/modified
3. Fill in `### Result` with divergence type breakdown and predicted new match count
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 6: Investigate Full Pipeline Match Divergence - <DATE>

**Branch:** `planning/sprint20-task6`

#### Summary
<2–4 sentences: divergence type breakdown, predicted match count improvement from .l fix, tolerance finding>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 5.1, 5.2, 5.3, 5.4 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 6 → COMPLETE
```

## Quality Gate
Documentation/research only. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md
  grep -c "^|" docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md

If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 6: Investigate pipeline match divergence

- Create PIPELINE_MATCH_ANALYSIS.md: 16 non-matching models classified
- Predicted new match count after .l emission: X (was 9)
- Verify KNOWN_UNKNOWNS 5.1, 5.2, 5.3, 5.4
- Update PREP_PLAN.md Task 6 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task6
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 6: Investigate Full Pipeline Match Divergence" \
    --body "## Summary
Completes Sprint 20 Prep Task 6 from PREP_PLAN.md.

## Deliverables
- [ ] PIPELINE_MATCH_ANALYSIS.md — 16 non-matching models classified by divergence type
- [ ] Predicted pipeline match count after .l emission fix
- [ ] KNOWN_UNKNOWNS.md — Unknowns 5.1, 5.2, 5.3, 5.4 verified
- [ ] PREP_PLAN.md Task 6 → COMPLETE

## Key Findings
<!-- Fill in: primary divergence cause, predicted match count, tolerance finding -->

## Unknowns Verified
- 5.1: Primary cause of 16-model solve/match gap
- 5.2: Tolerance calibration
- 5.3: .scale usage among non-matching models
- 5.4: Regression risk for 9 matching models"

Then wait for reviewer comments and address them before merging.
```

---

## Task 7 Prompt: Design Accounting Variable Detection (#764 mexss)

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 7: Design
Accounting Variable Detection (#764 mexss).

## Branch
Work on branch `planning/sprint20-task7`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task7

## Objective
Design the algorithm for detecting accounting/auxiliary variables in the IR. These are
variables that appear only as definitional identities (LHS of a single equality, no
objective contribution) and should not receive KKT stationarity equations. Evaluate
false positive risk before implementation.

## Background
From docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md:
- mexss has variables that are definitional aggregates (e.g., xmarket = sum(p, x(p)))
- Generating stationarity equations for these produces an over-constrained MCP
- The fix must be conservative: missing an accounting variable (model stays infeasible)
  is better than falsely excluding an optimization variable (silently wrong MCP)

Proposed three-criterion heuristic (to be validated):
1. Variable appears on the LHS of exactly one =E= equation
2. Variable does not appear in the objective equation (directly or through chain)
3. Variable's equation has the form v = f(other_vars) with no v on RHS

Read docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md first
for full context.

## What Needs to Be Done

1. Study mexss.gms to understand the accounting variable pattern:
   grep -A5 "=E=\|xmarket\|accounting" data/gamslib/raw/mexss.gms | head -50
   python -m src.cli data/gamslib/raw/mexss.gms 2>&1 | head -30

2. Inspect the ModelIR structure to understand what information is available for
   static analysis:
   python -c "
   import sys; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   ir = parse_file('data/gamslib/raw/mexss.gms')
   print([attr for attr in dir(ir) if not attr.startswith('_')])
   "

3. Check whether an existing dependency graph or equation-to-variable mapping exists:
   grep -n "dependency\|objective\|equation_map\|var_to_eq\|lhs\|rhs" \
     src/ir/ast.py src/kkt/stationarity.py | head -30

4. Formalize the detection algorithm with precise criteria. For each criterion, determine:
   - Can it be computed from the static IR? (yes/no)
   - What IR attributes/methods would be needed?
   - Computational cost?

5. Run the proposed heuristic mentally (or via code) against 3 currently-solving models
   to check for false positives. Pick models from: ajax, blend, demo1, himmel11, house,
   mathopt2, prodmix, rbrock, trnsport.

6. Check how many models in the corpus have sum-assignment patterns like mexss:
   grep -rl "=E=.*sum(" data/gamslib/raw/ | wc -l

7. Create `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` with:
   - mexss pattern characterization (exact variables, exact equations)
   - Formalized detection algorithm (3+ criteria with precise IR-level description)
   - Static analysis feasibility: yes/no per criterion, any that require dynamic analysis
   - False positive risk assessment on ≥3 solving models
   - Conservative vs. aggressive heuristic recommendation
   - Implementation location: file, function, approximate line
   - Corpus-wide impact estimate: how many models have similar patterns?

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 2.1: What is the precise structural pattern of accounting variables in mexss?
Update with: which specific variables are accounting variables, their equation structure,
whether they match all three proposed criteria.

### Unknown 2.2: Can accounting variables be reliably detected using only static IR analysis?
Update with: yes/no per criterion, whether a runtime dependency graph is needed, whether
deferring to Sprint 21 is recommended if static analysis is insufficient.

### Unknown 2.3: How many models beyond mexss would benefit from accounting variable detection?
Update with: count from grep, which of those are currently failing, expected additional models fixed.

### Unknown 2.4: Will accounting variable detection break any currently-solving model?
Update with: false positive risk assessment result for ≥3 models, whether the test suite
would catch regressions automatically.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 7:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created/modified
3. Fill in `### Result` with: algorithm formalized (conservative/aggressive), static
   analysis feasibility conclusion, false positive risk finding
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 7: Design Accounting Variable Detection - <DATE>

**Branch:** `planning/sprint20-task7`

#### Summary
<2–4 sentences: algorithm design, static vs. dynamic feasibility, false positive risk, implementation location>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md`** (created): <description>
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 2.1, 2.2, 2.3, 2.4 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 7 → COMPLETE
```

## Quality Gate
Documentation/research only. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md
  grep "Algorithm\|False Positive\|Criterion" \
    docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md | wc -l

If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 7: Design accounting variable detection

- Create ACCOUNTING_VAR_DETECTION_DESIGN.md: algorithm + false positive analysis
- Static analysis feasible: <yes/no>; recommendation: <conservative/aggressive>
- Verify KNOWN_UNKNOWNS 2.1, 2.2, 2.3, 2.4
- Update PREP_PLAN.md Task 7 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task7
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 7: Design Accounting Variable Detection (#764)" \
    --body "## Summary
Completes Sprint 20 Prep Task 7 from PREP_PLAN.md.

## Deliverables
- [ ] ACCOUNTING_VAR_DETECTION_DESIGN.md — algorithm design + false positive risk
- [ ] KNOWN_UNKNOWNS.md — Unknowns 2.1, 2.2, 2.3, 2.4 verified
- [ ] PREP_PLAN.md Task 7 → COMPLETE

## Key Findings
<!-- Fill in: algorithm, static analysis feasibility, false positive risk, implementation location -->

## Unknowns Verified
- 2.1: Precise mexss accounting variable pattern
- 2.2: Static IR analysis feasibility
- 2.3: Corpus-wide model count
- 2.4: False positive risk on currently-solving models"

Then wait for reviewer comments and address them before merging.
```

---

## Task 8 Prompt: Review Sprint 19 Retrospective Action Items

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 8: Review
Sprint 19 Retrospective Action Items.

## Branch
Work on branch `planning/sprint20-task8`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task8

## Objective
Review the "What Could Be Improved" section of the Sprint 19 retrospective. For each of
the 6 items, create a concrete action captured in Sprint 20 planning documents. Also
partially verify Unknowns 3.1 and 3.2 (chenery AD condition pattern) by reading the
chenery issue file.

## Background
Read docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md, specifically the
"What Could Be Improved" section. The 6 improvement items are:
1. Full pipeline match target missed — conservative targets, "within ε" as leading indicator
2. `lop` exclusion not documented — document denominator changes with dated sprint log entry
3. Day 13 validation exposed 5 issues late — run model validation earlier (Day 10–11)
4. `#671` premature "not fixable" assessment — smoke test before declaring
5. Parse rate denominator confusion — use gamslib_status.json count directly
6. Deferred issues accumulating — consider a dedicated "solver quality" sprint

Also read docs/issues/ISSUE_763_chenery-mcp-division-by-zero-del-parameter.md to
understand the AD condition propagation pattern for Unknowns 3.1 and 3.2.

## What Needs to Be Done

1. Read the full Sprint 19 retrospective "What Could Be Improved" section.

2. For each of the 6 items, define a concrete action and determine where it should be
   captured (PREP_PLAN.md Task 10, Sprint 20 PLAN.md, or a process note):
   - Item 1: How to track "within ε" as a leading indicator in Sprint 20?
   - Item 2: What specific process step prevents undocumented denominator changes?
   - Item 3: Which day in Sprint 20 should model validation be scheduled?
   - Item 4: What is the smoke-test checklist for "not fixable" declarations?
   - Item 5: What is the exact sprint-start baseline process?
   - Item 6: Should a "solver quality" sprint be added to Epic 4 PROJECT_PLAN.md?

3. For Unknowns 3.1 and 3.2 (chenery AD condition):
   - Read docs/issues/ISSUE_763_chenery-mcp-division-by-zero-del-parameter.md
   - Determine: is the `$` condition inline (within expression) or equation-level?
   - Check what GAMS error the generated MCP produces
   - Look for existing DollarConditional handling in AD:
     grep -n "DollarConditional\|condition\|dollar" src/ad/derivative_rules.py | head -20
   - This is a *partial* verification only — full verification requires running chenery.gms

4. Create a brief action summary document (optional — can be notes in KNOWN_UNKNOWNS.md
   instead) or directly update KNOWN_UNKNOWNS.md and note the actions in PREP_PLAN.md
   Result section.

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 3.1: What is the exact form of the $ condition in chenery? (partial)
Update with: what the chenery issue file says about the condition form (inline vs. equation-level),
what error the MCP produces. Mark as `⚠️ Status: PARTIAL — full verification requires running chenery.gms`.

### Unknown 3.2: Does the AD system have any existing mechanism for condition propagation? (partial)
Update with: what grep reveals about DollarConditional handling in src/ad/derivative_rules.py,
whether there is any existing propagation concept. Mark as `⚠️ Status: PARTIAL`.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 8:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files modified
3. Fill in `### Result` with: all 6 retrospective items actioned, concrete action per item,
   where each action is captured; Unknowns 3.1 and 3.2 partially verified
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 8: Review Sprint 19 Retrospective Action Items - <DATE>

**Branch:** `planning/sprint20-task8`

#### Summary
<2–4 sentences: all 6 retrospective items actioned, key process changes, partial chenery verification>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknowns 3.1, 3.2 partially verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 8 → COMPLETE, retrospective actions captured
```

## Quality Gate
Documentation/research only. No Python files expected to change.
If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 8: Review Sprint 19 retrospective actions

- Action all 6 retrospective improvement items with concrete Sprint 20 actions
- Partially verify KNOWN_UNKNOWNS 3.1, 3.2 (chenery AD condition)
- Update PREP_PLAN.md Task 8 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task8
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 8: Review Sprint 19 Retrospective Action Items" \
    --body "## Summary
Completes Sprint 20 Prep Task 8 from PREP_PLAN.md.

## Deliverables
- [ ] All 6 Sprint 19 retrospective improvement items actioned
- [ ] Each item has a concrete Sprint 20 action with a home (PLAN.md, PREP_PLAN, process note)
- [ ] KNOWN_UNKNOWNS.md — Unknowns 3.1, 3.2 partially verified
- [ ] PREP_PLAN.md Task 8 → COMPLETE

## Retrospective Actions
<!-- Fill in: 1-line action for each of the 6 items -->

## Unknowns Verified
- 3.1: Chenery $ condition form (partial)
- 3.2: AD system condition propagation mechanism (partial)"

Then wait for reviewer comments and address them before merging.
```

---

## Task 9 Prompt: Snapshot Baseline Metrics

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 9: Snapshot
Baseline Metrics.

## Branch
Work on branch `planning/sprint20-task9`. Create it from `main`:
  git checkout main 
  git checkout -b planning/sprint20-task9

## Objective
Run the full pipeline on all models and record exact baseline metrics for Sprint 20,
pinned to a timestamped snapshot with an explicit denominator record. This prevents
the denominator confusion that affected Sprint 19 metrics. Also confirm the 27
lexer_invalid_char count (Unknown 4.2 — may already be verified by Task 3).

## Background
Sprint 19 final state (to be confirmed):
- Parse: 107/160 tested (66.9%)
- lexer_invalid_char: 27
- internal_error (pipeline): 6
- Translate success: 73
- Solve success: 25
- Full pipeline match: 9
- Test count: 3,579
- Total catalog: 219; tested: 160; excluded: 59

The snapshot must be taken after all prep tasks that might involve code changes
(Tasks 2–8) are complete. If this is being run before Tasks 2–8 are merged, ensure
you are on the clean `main` base (no code changes).

## What Needs to Be Done

1. Ensure you are on the correct branch and all tests pass:
   git status
   make test

2. Run the full pipeline retest:
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet

3. Record the key metrics from the output (parse rate, error categories, solve, match).
   Also query gamslib_status.json directly for precise counts:
   python -c "
   import json
   from collections import Counter
   with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
   models = data.get('models', [])
   parse_statuses = Counter(m.get('nlp2mcp_parse', {}).get('status', 'not_tested') for m in models)
   translate_statuses = Counter(m.get('nlp2mcp_translate', {}).get('status', 'not_tested') for m in models)
   solve_statuses = Counter(m.get('mcp_solve', {}).get('status', 'not_tested') for m in models)
   match_counts = Counter(m.get('solution_comparison', {}).get('objective_match') for m in models)
   print('Parse:', dict(sorted(parse_statuses.items())))
   print('Translate:', dict(sorted(translate_statuses.items())))
   print('Solve:', dict(sorted(solve_statuses.items())))
   print('Match (True=match, False=mismatch, None=not tested):', dict(sorted(match_counts.items(), key=lambda x: str(x[0]))))
   "

4. Record the git commit SHA:
   git rev-parse HEAD

5. Record explicit denominator information:
   - Total catalog: 219 models
   - Tested: N (those in gamslib_status.json with a pipeline result)
   - Excluded: 219 - N (with reason: compilation errors, license limits, infeasibility, etc.)
   - List excluded models individually if feasible

6. Create `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md` with:
   - Snapshot date and git commit SHA
   - All metric counts in a table
   - Explicit denominator section
   - Any discrepancies vs. Sprint 19 final state explained
   - Excluded models list with reasons

## Known Unknowns to Verify
Update `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`:

### Unknown 4.2: Are there lexer_invalid_char models already fixed by Sprint 19 but not yet re-run?
Update with: actual lexer_invalid_char count from the fresh retest. If it's still 27, mark VERIFIED.
If it's fewer, mark WRONG with the actual count.
(Note: This may already be verified by Task 3. If so, confirm the count matches.)

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 9:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with files created
3. Fill in `### Result` with all metrics (one-liner summary matching the BASELINE_METRICS.md table)
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 9: Snapshot Baseline Metrics - <DATE>

**Branch:** `planning/sprint20-task9`

#### Summary
Sprint 20 baseline: parse N/M tested (X%), lexer_invalid_char N, internal_error N,
translate N, solve N, full pipeline match N, tests N. Snapshot at commit <SHA>.

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`** (created): timestamped baseline snapshot
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): Unknown 4.2 verified
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 9 → COMPLETE
```

## Quality Gate
This task should NOT involve any Python source changes. The pipeline retest may take
several minutes. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md
  grep "Parse\|Translate\|Solve\|Test count\|Baseline date" \
    docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 9: Snapshot baseline metrics

- Create BASELINE_METRICS.md: parse N/M (X%), solve N, match N, tests N
- Baseline at commit <SHA>, <DATE>
- Verify KNOWN_UNKNOWNS 4.2 (lexer_invalid_char count: N)
- Update PREP_PLAN.md Task 9 -> COMPLETE
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task9
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 9: Snapshot Baseline Metrics" \
    --body "## Summary
Completes Sprint 20 Prep Task 9 from PREP_PLAN.md.

## Deliverables
- [ ] BASELINE_METRICS.md — timestamped snapshot with explicit denominator
- [ ] KNOWN_UNKNOWNS.md — Unknown 4.2 verified (lexer_invalid_char count)
- [ ] PREP_PLAN.md Task 9 → COMPLETE

## Baseline Metrics
<!-- Fill in after running retest:
- Parse: N/M tested (X%)
- lexer_invalid_char: N
- internal_error: N
- Translate success: N
- Solve success: N
- Full pipeline match: N
- Test count: N
- Git SHA: <sha>
-->"

Then wait for reviewer comments and address them before merging.
```

---

## Task 10 Prompt: Plan Sprint 20 Detailed Schedule

```
You are working on the nlp2mcp project. Your task is Sprint 20 Prep Task 10: Plan
Sprint 20 Detailed Schedule.

## Branch
Work on branch `planning/sprint20-task10`. Create it from `main`
AFTER Tasks 2–9 have been merged into `main`:
  git checkout main 
  git pull origin main 
  git checkout -b planning/sprint20-task10

## Objective
Create `docs/planning/EPIC_4/SPRINT_20/PLAN.md` with a day-by-day Sprint 20 schedule
incorporating all findings from Tasks 1–9. The plan must have revised effort estimates
(based on actual prep findings, not PROJECT_PLAN.md guesses), two checkpoints with
GO/NO-GO criteria, specific acceptance criteria (numbers, not vague), and at least
two contingency plans.

## Background
Before starting, read these documents to gather all findings:
- docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md — all Tasks 2–9 Results sections
- docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md — all verified unknowns
- docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md — IndexOffset revised estimate
- docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md — lexer priorities
- docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md — .l emission fix design
- docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md — translate error count
- docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md — match divergence analysis
- docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md — algorithm design
- docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md — confirmed baseline numbers
- docs/planning/EPIC_4/SPRINT_19/PLAN.md — PLAN.md format reference
- docs/planning/EPIC_4/PROJECT_PLAN.md lines 268–385 — Sprint 20 project scope

Also check the Sprint 19 retrospective for process improvements to incorporate:
- docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md

## What Needs to Be Done

1. Aggregate effort estimates from all prep tasks:
   - IndexOffset: original ~4h → revised Xh (from Task 2)
   - .l emission: original ~2h → revised Xh (from Task 4)
   - Accounting variable detection: medium effort → Xh (from Task 7)
   - AD condition propagation (chenery): original ~6–8h → Xh (informed by Task 8)
   - lexer_invalid_char: target +10–15 → Xh for top subcategories (from Task 3)
   - Translate errors: original 6–8h → Xh for N models (from Task 5)
   - Pipeline match improvement: driven by .l emission (from Task 6)

2. Right-size the sprint scope. The total must fit in ~15 sprint days. Deprioritize or
   defer any items where prep findings show the effort exceeds the budget.

3. Design the day-by-day schedule following the Sprint 19 PLAN.md format:
   - Day 0: baseline confirm + sprint kickoff
   - Days 1–N: highest-priority fixes
   - Checkpoint 1 (Day 6): .l emission + IndexOffset complete; assess solve rate
   - Days N+1–M: lexer grammar work, accounting vars, translate errors
   - Checkpoint 2 (Day 11): lexer fixes done; model validation; GO/NO-GO for remaining
   - Days M+1–13: pipeline match investigation, tolerance, remaining fixes
   - Day 14: sprint close, retrospective

4. Incorporate Sprint 19 retrospective process improvements:
   - Schedule model validation for Day 10–11 (not Day 13)
   - Add smoke-test checklist note for "not fixable" declarations
   - Track "models within ε" as leading indicator for pipeline match
   - Baseline denominator explicitly documented (Task 9 result)

5. Define two checkpoints with GO/NO-GO criteria (specific numbers):
   - Checkpoint 1 (Day 6): e.g., "solve count ≥ N, .l emission PR merged"
   - Checkpoint 2 (Day 11): e.g., "lexer_invalid_char ≤ N, model validation run"

6. Define acceptance criteria for each workstream (use numbers from baseline + targets):
   - Parse rate: ≥ X/160 (≥ X%)
   - lexer_invalid_char: ≤ N
   - Solve success: ≥ N models
   - Full pipeline match: ≥ N models
   - Translate errors: ≤ N

7. Document at least 2 contingency plans (scope reduction if behind at Checkpoint 1/2).

8. Create `docs/planning/EPIC_4/SPRINT_20/PLAN.md` following the format of
   docs/planning/EPIC_4/SPRINT_19/PLAN.md (read it first for structure).

9. Review all KNOWN_UNKNOWNS.md entries. Flag any still marked INCOMPLETE or PARTIAL
   that were not fully verified by Tasks 2–9. Document these as open risks in PLAN.md.

## PREP_PLAN.md Updates
Update `docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md` Task 10:
1. Change status to `✅ COMPLETE`
2. Fill in `### Changes` with PLAN.md created and any other files modified
3. Fill in `### Result` with 1–3 sentences: sprint scope confirmed, key effort revisions,
   checkpoint criteria
4. Check off all acceptance criteria (`- [ ]` → `- [x]`)

Also update the PREP_PLAN.md Summary section:
- All 10 tasks should now be ✅ COMPLETE
- Add a "Prep Phase Complete" note at the top

## CHANGELOG.md Update
Add at the top of `## [Unreleased]`:

```
### Sprint 20 Prep Task 10: Plan Sprint 20 Detailed Schedule - <DATE>

**Branch:** `planning/sprint20-task10`

#### Summary
<2–4 sentences: PLAN.md created, revised effort estimates, key scope decisions,
checkpoint criteria>

#### Planning Documents
- **`docs/planning/EPIC_4/SPRINT_20/PLAN.md`** (created): day-by-day Sprint 20 schedule
- **`docs/planning/EPIC_4/SPRINT_20/PREP_PLAN.md`** (updated): Task 10 → COMPLETE; all 10 tasks done
- **`docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`** (updated): remaining INCOMPLETE items flagged as risks
```

## Quality Gate
Documentation-only task. Verify:
  ls docs/planning/EPIC_4/SPRINT_20/PLAN.md
  grep -c "^## Day" docs/planning/EPIC_4/SPRINT_20/PLAN.md
  grep "Checkpoint" docs/planning/EPIC_4/SPRINT_20/PLAN.md | wc -l

Both commands should return ≥ 1. The Day count should be 15 (Day 0 through Day 14).

If Python files were modified: make typecheck && make lint && make format && make test

## Commit Message Format
  git add -A
  git commit -m "Complete Sprint 20 Prep Task 10: Create Sprint 20 PLAN.md

- Create PLAN.md: Day 0–14 schedule, 2 checkpoints, revised effort estimates
- IndexOffset: Xh, .l emission: Xh, lexer: Xh, accounting vars: Xh
- Sprint 20 targets: parse ≥ X%, solve ≥ N, match ≥ N
- All KNOWN_UNKNOWNS flagged or verified
- Update PREP_PLAN.md Task 10 -> COMPLETE (all 10 tasks done)
- Update CHANGELOG.md"

## Pull Request
  git push origin planning/sprint20-task10
  gh pr create \
    --base main \
    --title "Sprint 20 Prep Task 10: Plan Sprint 20 Detailed Schedule" \
    --body "## Summary
Completes Sprint 20 Prep Task 10 — the final prep task. Creates PLAN.md with
the complete day-by-day Sprint 20 schedule based on all prep task findings.

## Deliverables
- [ ] PLAN.md — Day 0 through Day 14 schedule
- [ ] Two checkpoints with GO/NO-GO criteria (specific numbers)
- [ ] Revised effort estimates for all workstreams
- [ ] At least 2 contingency plans
- [ ] Sprint 19 retrospective process improvements incorporated
- [ ] All KNOWN_UNKNOWNS verified or flagged as risks
- [ ] PREP_PLAN.md — all 10 tasks COMPLETE
- [ ] CHANGELOG.md updated

## Sprint 20 Targets (to be filled in)
- Parse rate: ≥ ?/160 (?%)
- lexer_invalid_char: ≤ ?
- Solve success: ≥ ?
- Full pipeline match: ≥ ?

## Key Scope Decisions
<!-- Fill in: any items deferred vs. PROJECT_PLAN.md, revised effort revisions -->

## All KNOWN_UNKNOWNS Verified
<!-- Confirm: all 26 unknowns are ✅ VERIFIED, ❌ WRONG, or ⚠️ PARTIAL with risk noted -->"

Then wait for reviewer comments and address them before merging.
Once merged, Sprint 20 prep is complete and Sprint 20 Day 1 can begin.
```
