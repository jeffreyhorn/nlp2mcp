# Sprint 21 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 21 (Days 0–14). Each prompt is designed to be used when starting work on that specific day.

**Sprint Duration:** 15 days (Day 0 – Day 14)
**Estimated Effort:** ~48–58 hours (~3.2–3.9h/day effective capacity)
**Baseline:** parse 132/160 (82.5%), translate 123/132 (93.2%), solve 33/124 (26.6%), match 16/33 (48.5%), tests 3,715

---

## Day 0 Prompt: Baseline Confirm + Sprint Kickoff

**Branch:** Create a new branch named `sprint21-day0-kickoff` from `main`

**Objective:** Verify clean baseline, internalize the plan, confirm all tests pass, initialize sprint log with error category breakdown.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/PLAN.md` (lines 1–50) — sprint overview, targets, and workstream summaries
- Read `docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md` — exact baseline numbers at commit `feffaa95`
- Read `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md` — note Category 1 unknowns (1.1-1.4) are NOT YET VERIFIED (Task 2 incomplete)

**Tasks to Complete (~1 hour):**

1. **Verify baseline** (0.25h)
   - Run `make test` — must show 3,715+ passed, 0 failed
   - Run `git log --oneline -5` — confirm you are on a clean commit from `main`

2. **Initialize SPRINT_LOG.md** (0.25h)
   - Copy the template from `docs/planning/EPIC_4/SPRINT_21/SPRINT_LOG.md`
   - Record baseline metrics: parse 132/160, translate 123/132, solve 33/124, match 16/33, tests 3,715
   - Record baseline error category breakdown (PR5 compliance):
     - **Parse-stage:** lexer_invalid_char (10), internal_error (7), semantic_undefined_symbol (7), parser_invalid_expression (3), model_no_objective_def (1)
     - **Solve-stage:** path_syntax_error (48), path_solve_terminated (29), model_infeasible (12), path_solve_license (2)
   - Note baseline commit: `feffaa95`

3. **Run full pipeline parse retest (PR3 compliance)** (0.25h)
   - Run: `.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet`
   - Verify parse count matches baseline (132/160)
   - This uses `parse_model_file()` + `validate_model_structure()`, not `parse_file()` alone

4. **Review Day 1 tasks** (0.25h)
   - Read `SEMANTIC_ERROR_AUDIT.md` — understand the 7 models and their fixes
   - Identify the FUNCNAME regex line in `src/gams/gams_grammar.lark`

**Deliverables:**
- `make test` passing (3,715+ tests)
- SPRINT_LOG.md initialized with baseline metrics and error category breakdown
- Pipeline parse retest verified (132/160)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] `make test` passes (3,715+ tests)
- [ ] SPRINT_LOG.md created with baseline metrics and error category breakdown (PR5)
- [ ] Pipeline parse retest verified via `parse_model_file()` + `validate_model_structure()` (PR3)
- [ ] Mark Day 0 as complete in PLAN.md
- [ ] Log progress to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create PR: `gh pr create --title "Sprint 21 Day 0: Baseline Confirm + Sprint Kickoff" --body "..." --base main`
2. **Record PR number in SPRINT_LOG.md immediately after creation (PR2)**
3. Request Copilot review: `gh pr edit --add-reviewer copilot`
4. Address review comments; reply using `gh api "repos/jeffreyhorn/nlp2mcp/pulls/NNN/comments/$id/replies" -X POST -f body="..."`

---

## Day 1 Prompt: WS1 — Semantic Error Resolution (+7 parse)

**Branch:** Create a new branch named `sprint21-day1-semantic-errors` from `main`

**Objective:** Add 4 missing GAMS built-in functions to FUNCNAME, add acronym handler, fix sameas string literal handling. This unblocks 7 parse-failing models and exceeds the ≥135/160 parse target on Day 1.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/SEMANTIC_ERROR_AUDIT.md` — full per-model analysis
- Read `src/gams/gams_grammar.lark` — find the FUNCNAME terminal regex (line ~797)
- Read `src/ir/parser.py` — find the `acronym_stmt` rule (grammar line ~650) and understand that no handler exists yet
- Read `src/ir/parser.py` — find condition handling for `sameas()` calls

**Tasks to Complete (~3-4 hours):**

1. **Add 4 functions to FUNCNAME regex** (0.5h)
   - In `src/gams/gams_grammar.lark`, add `sign|centropy|mapval|betareg` to the FUNCNAME terminal
   - This single change unblocks 5 models: camcge, feedtray, cesam2, sambal, procmean
   - Verify: each model should now parse past the previously-failing line

2. **Add `acronym_stmt` handler to IR builder** (1-2h)
   - In `src/ir/parser.py`, add a visitor method for the `acronym_stmt` grammar rule
   - Register each acronym name as a known symbol (e.g., as a special constant or zero-valued parameter)
   - Test with `worst.gms` which uses `Acronym future, call, puto;`

3. **Fix sameas string literal handling** (1h)
   - In `src/ir/parser.py`, find where `sameas()` conditions are evaluated during semantic validation
   - Fix to accept quoted string literals (e.g., `"ROW"`) as set element name references, not as undeclared symbols
   - Test with `cesam.gms` which uses `$(not sameas(ii,"ROW"))`

4. **Unit tests** (1h)
   - Test FUNCNAME with each new function: `sign(x)`, `centropy(x,y)`, `mapval(x)`, `betareg(x,a,b)`
   - Test acronym declaration and usage in conditional expressions
   - Test sameas with string literal argument
   - ≥5 new tests total

5. **Run newly-parsing models through full pipeline (PR4)** (0.5h)
   - For each of the 7 newly-parsing models, run through full pipeline:
     ```python
     import sys; sys.setrecursionlimit(50000)
     from src.ir.parser import parse_model_file
     for m in ['camcge', 'feedtray', 'cesam2', 'sambal', 'procmean', 'worst', 'cesam']:
         try:
             parse_model_file(f'data/gamslib/raw/{m}.gms')
             print(f'{m}: PARSE OK')
         except Exception as e:
             print(f'{m}: {type(e).__name__}: {e}')
     ```
   - Record translate/solve status for each

**Deliverables:**
- Grammar updated with 4 new FUNCNAME entries
- IR builder acronym handler implemented
- sameas string literal fix implemented
- ≥5 unit tests
- Pipeline status recorded for 7 newly-parsing models

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] parse ≥ 139/160 (7 semantic_undefined_symbol models resolved)
- [ ] semantic_undefined_symbol = 0
- [ ] ≥5 new unit tests
- [ ] All 7 newly-parsing models tested through full pipeline (PR4)
- [ ] Mark Day 1 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md with Day 1 metrics
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run 7 newly-parsing models through full pipeline and record results (PR4)

**Pull Request & Review:**
1. Create PR: `gh pr create --title "Sprint 21 Day 1: Semantic Error Resolution (+7 parse)" --body "..." --base main`
2. **Record PR number in SPRINT_LOG.md immediately (PR2)**
3. Request Copilot review
4. Address comments; reply to each individually

---

## Day 2 Prompt: WS2 — Macro Expansion Part 1 (Design + Core)

**Branch:** Create a new branch named `sprint21-day2-macro-expansion` from `main`

**Objective:** Design and implement the core macro expansion subsystem: `$set`/`$setglobal` directives and `%name%` expansion. Implement `%system.nlp%` for saras.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md` Category 1 — unknowns 1.1-1.4 (NOT YET VERIFIED)
- Read `src/ir/preprocessor.py` — understand `strip_unsupported_directives()` and current directive handling
- Read `data/gamslib/raw/saras.gms` (if available) — identify `%system.nlp%` usage
- Read `data/gamslib/raw/springchain.gms` (if available) — identify `$set`/`$eval`/`%N%` usage
- Read `docs/issues/ISSUE_837_springchain-bracket-expr-scalar-data.md` and `docs/issues/ISSUE_840_saras-system-nlp-macro.md`

**Tasks to Complete (~3-4 hours):**

1. **Design macro store** (0.5-1h)
   - Create a `MacroStore` class (or dict-based store) for compile-time macro values
   - Support local (`$set`) and global (`$setglobal`) scopes
   - Support case-insensitive lookup for `%name%` expansion
   - Define system macro registry with `%system.nlp%` = `"CONOPT"` (or appropriate default)

2. **Implement `$set name value` / `$setglobal name value`** (1-1.5h)
   - Parse `$set` and `$setglobal` directives in the preprocessor
   - Store name→value mappings in the MacroStore
   - Remove the directive line from output (already happens via `strip_unsupported_directives`)

3. **Implement `%name%` expansion** (1h)
   - After all directives are processed, expand `%name%` references in source lines
   - Case-insensitive matching
   - Handle undefined macros: emit warning, leave unexpanded (or raise error)
   - Test with `%system.nlp%` → `"CONOPT"`

4. **Unit tests** (0.5-1h)
   - Test `$set` stores value; `%name%` expands to stored value
   - Test case-insensitive expansion
   - Test `%system.nlp%` expansion
   - Test undefined macro handling
   - ≥5 new tests

5. **Verify saras** (0.25h)
   - Run saras through preprocessor and check `%system.nlp%` expansion
   - Run through `parse_model_file()` to verify it parses

**Deliverables:**
- MacroStore implementation in `preprocessor.py`
- `$set`/`$setglobal`/`%name%` expansion working
- `%system.nlp%` system macro implemented
- ≥5 unit tests
- saras parse status verified

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] MacroStore implemented with local/global scope
- [ ] `$set`/`$setglobal` directives parsed and stored
- [ ] `%name%` expansion functional (case-insensitive)
- [ ] `%system.nlp%` system macro works
- [ ] saras parses (if `%system.nlp%` is the only blocker)
- [ ] ≥5 new unit tests
- [ ] Mark Day 2 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run saras through full pipeline and record results (PR4)

---

## Day 3 Prompt: WS2 — Macro Expansion Part 2 ($eval + springchain)

**Branch:** Create a new branch named `sprint21-day3-macro-eval` from `main`

**Objective:** Implement `$eval` arithmetic evaluation; verify springchain end-to-end. Complete macro expansion workstream.

**Prerequisites:**
- Read Day 2 implementation — understand MacroStore and `%name%` expansion
- Read `data/gamslib/raw/springchain.gms` — `$set N 10`, `$set NM1 9`, `$eval N2 %N%-2`
- The key question (Unknown 1.1): Is simple integer arithmetic sufficient for `$eval`? springchain uses `%N%-2` which is subtraction of integer constants.

**Tasks to Complete (~3-4 hours):**

1. **Implement `$eval name expression`** (1-2h)
   - Parse `$eval` directive: evaluate the expression and store result in MacroStore
   - Expression evaluation scope: at minimum, integer arithmetic (`+`, `-`, `*`, `/`)
   - The expression may contain `%macro%` references that need to be expanded first
   - Example: `$eval N2 %N%-2` → expand `%N%` to `10` → evaluate `10-2` → store `N2 = 8`

2. **Handle expansion ordering** (0.5h)
   - Ensure `%name%` references in `$eval` expressions are expanded before evaluation
   - Handle forward references gracefully (error if macro referenced before definition)

3. **Verify springchain** (0.5h)
   - Run springchain through preprocessor; verify `%N%` → `10`, `%NM1%` → `9`, `%N2%` → `8`
   - Run through `parse_model_file()` to verify it parses
   - Run through full pipeline to check translate/solve status

4. **End-to-end verification** (0.5h)
   - Both saras and springchain through full pipeline
   - Record lexer_invalid_char count (should be ≤8 after removing saras + springchain)

5. **Edge case tests** (0.5-1h)
   - Nested expansion: `$set A foo`, `$set B %A%bar` → `%B%` = `foobar`
   - Multiple `$eval` chaining
   - Undefined macro in `$eval` expression
   - ≥3 new tests

**Deliverables:**
- `$eval` implementation with integer arithmetic evaluation
- springchain and saras both parse
- lexer_invalid_char ≤ 8
- ≥3 new unit tests

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `$eval` functional with integer arithmetic
- [ ] springchain parses via `parse_model_file()`
- [ ] saras parses (confirmed from Day 2)
- [ ] lexer_invalid_char ≤ 8 (saras + springchain removed from lexer errors)
- [ ] ≥3 new unit tests
- [ ] Mark Day 3 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run springchain + saras through full pipeline and record results (PR4)

---

## Day 4 Prompt: WS3 — internal_error Lead/Lag Fix (3 models)

**Branch:** Create a new branch named `sprint21-day4-leadlag-params` from `main`

**Objective:** Extend `_extract_indices()` to handle lead/lag syntax in parameter assignments. This unblocks imsl, sarf, tfordy (3 models with one fix).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md` Section 2.2 (imsl), 2.4 (sarf), 2.6 (tfordy)
- Read `src/ir/parser.py` — find `_extract_indices()` (line ~610-614) where `lag_lead_suffix` is rejected
- Read Section 4 (Lead/Lag Analysis Summary) for consolidated usage patterns

**Tasks to Complete (~2-3 hours):**

1. **Extend `_extract_indices()` for lead/lag in parameter context** (1-1.5h)
   - Currently raises error at line 610-614 when encountering `lag_lead_suffix`
   - Extract the base index and lag/lead offset expression
   - Store the offset information in the IR (e.g., as `IndexOffset` objects)
   - Handle all variants: linear lead (`+N`), linear lag (`-N`), circular lead (`++expr`), circular lag (`--expr`)

2. **Handle complex offset expressions** (0.5-1h)
   - imsl: `m+floor((ord(n)-1)/k)` — function call in offset
   - sarf: `t++(cs(c,"start",s)-1)` — circular lead with complex expression
   - tfordy: `te+3`, `t-1`, `t-2` — simple integer offsets

3. **Unit tests** (0.5h)
   - Test linear lead in parameter assignment: `x(t+1) = expr`
   - Test linear lag: `x(t-1) = expr`
   - Test circular lead: `x(t++expr) = expr`
   - Test complex offset with function call
   - ≥4 new tests

4. **Verify models** (0.25h)
   - Run imsl, sarf, tfordy through `parse_model_file()`
   - Run through full pipeline to check translate/solve status

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `_extract_indices()` handles lead/lag in parameter assignments
- [ ] imsl, sarf, tfordy all parse via `parse_model_file()`
- [ ] internal_error ≤ 4
- [ ] ≥4 new unit tests
- [ ] Mark Day 4 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run imsl, sarf, tfordy through full pipeline and record results (PR4)

---

## Day 5 Prompt: CHECKPOINT 1 + WS3 internal_error (if-stmt + table)

**Branch:** Create a new branch named `sprint21-day5-checkpoint1-internal-error` from `main`

**Objective:** Run Checkpoint 1 pipeline retest with error category breakdown; fix senstran (if-stmt) and turkpow (table dotted index).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md` Section 2.5 (senstran), 2.7 (turkpow)
- Read `src/ir/parser.py` — `_handle_if_stmt` (line ~3392) and `_parse_param_data_items` (line ~5042)

**Tasks to Complete (~4 hours):**

1. **CHECKPOINT 1: Full pipeline retest (PR3 + PR5)** (1h)
   - Run: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record in SPRINT_LOG.md:
     - Parse count (expect ≥141/160)
     - Parse error breakdown (PR5): lexer_invalid_char, internal_error, semantic_undefined_symbol, parser_invalid_expression, model_no_objective_def
     - Solve error breakdown (PR5): path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license
     - Solve count, match count
   - Run `make test` — record test count

2. **Fix senstran: bare identifier as `if` condition** (1.5-2h)
   - In `_handle_if_stmt`, update to recognize a bare identifier (e.g., `pors`) as a valid condition expression
   - May need minor grammar adjustment or just IR builder handler update
   - Test: `if(pors, ...)` where `pors` is a scalar parameter set to 1

3. **Fix turkpow: table row dotted index** (1-1.5h)
   - In `_parse_param_data_items`, handle dotted index notation for multi-dimensional parameters
   - Split `hydro-4.1978` into `('hydro-4', '1978')` based on declared domain cardinality
   - Test: `Parameter hlo(m,te) / hydro-4.1978 250 /`

4. **Unit tests** (0.5h)
   - Test `if(scalar_param, ...)` condition
   - Test dotted index in parameter data
   - ≥3 new tests

5. **Verify models through full pipeline (PR4)** (0.25h)
   - Run senstran, turkpow through full pipeline

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Checkpoint 1 metrics recorded with full error category breakdown (PR5)
- [ ] Pipeline retest used `parse_model_file()` + `validate_model_structure()` (PR3)
- [ ] senstran parses
- [ ] turkpow parses
- [ ] internal_error ≤ 2
- [ ] ≥3 new unit tests
- [ ] Mark Day 5 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md with Checkpoint 1 metrics
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record Checkpoint 1 metrics with error category breakdown in SPRINT_LOG.md (PR5)
- [ ] Run senstran, turkpow through full pipeline and record results (PR4)

---

## Day 6 Prompt: WS4 — path_syntax_error Emitter Fixes (E + D)

**Branch:** Create a new branch named `sprint21-day6-emitter-fixes` from `main`

**Objective:** Fix set index quoting (Subcategory E, 7 models) and negative exponent parenthesization (Subcategory D, 3 models) in the emitter.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` Sections 2.4 (D) and 2.5 (E)
- Read `src/emit/emit_gams.py` — find where parameter indices are quoted and where expressions with `**` are formatted

**Tasks to Complete (~2-3 hours):**

1. **Fix set index quoting (Subcategory E)** (1-1.5h)
   - When emitting parameter indexing like `SAM("TRF",J)`, distinguish between:
     - String literals: keep quoted (e.g., `"TRF"`)
     - Set references: emit as bare identifiers (e.g., `J` not `"J"`)
   - Check if the index position matches a declared set name → bare identifier
   - 7 models affected: irscge, lrgcge, moncge, quocge, sample, stdcge, twocge (6 CGE models + sample)

2. **Fix negative exponent parenthesization (Subcategory D)** (0.5h)
   - In expression formatting, detect `** -N` patterns
   - Wrap negative numeric literals in parentheses: `** (-0.9904)`
   - 3 models affected: launch, ps2_f_eff, ps2_f_inf

3. **Unit tests** (0.5h)
   - Test set reference vs string literal in parameter indices
   - Test negative exponent formatting
   - ≥4 new tests

4. **Re-run affected models through full pipeline (PR4)** (0.5h)
   - Run all 10 models through GAMS compilation + PATH solve
   - Record which now compile cleanly and which have remaining errors

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Set index quoting fixed (7 CGE models compile cleanly)
- [ ] Negative exponent parenthesization fixed (3 models compile cleanly)
- [ ] ≥4 new unit tests
- [ ] All 10 models tested through full pipeline (PR4)
- [ ] Mark Day 6 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run all 10 affected models through full pipeline and record results (PR4)

---

## Day 7 Prompt: WS4 — Table Data Capture Part 1

**Branch:** Create a new branch named `sprint21-day7-table-data` from `main`

**Objective:** Begin implementing Table data capture in the IR builder so that `Table` declarations populate `ParameterDef.values`.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` Section 2.1 (Subcategory A, 16 models)
- Read `src/ir/parser.py` — find Table handling (search for `table` or `Table` in grammar rules)
- Read `src/gams/gams_grammar.lark` — find `table_stmt` or `table_data` rules
- Read a sample Table from a GAMS file (e.g., iobalance's `Table z1(i,j)`)

**Tasks to Complete (~3-4 hours):**

1. **Analyze Table data format** (0.5h)
   - Standard format: header row with column indices, data rows with row index + values
   - Dotted indices: `hydro-4.1978` for multi-dimensional tables
   - Edge cases: empty cells, string elements, trailing semicolons

2. **Implement Table data parsing** (2-2.5h)
   - Parse column headers from the Table declaration
   - Parse data rows: extract row index and map values to column indices
   - Store parsed data in `ParameterDef.values` (same format as inline parameter data)
   - Handle the standard `Table param(i,j) / header1 header2 ... / row1 v1 v2 ... /` format

3. **Unit tests** (0.5-1h)
   - Test standard Table parsing (2D, 3D)
   - Test dotted index format
   - Test empty cell handling
   - ≥3 new tests

4. **Verify on sample models** (0.25h)
   - Check that iobalance's `z1`, qdemo7's `alpha`, hydro's table data now populate `ParameterDef.values`

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Table data parsing implemented for standard format
- [ ] `ParameterDef.values` populated for at least 3 Subcategory A models
- [ ] ≥3 new unit tests
- [ ] Mark Day 7 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

## Day 8 Prompt: WS4 — Table Data Capture Part 2 + Test

**Branch:** Create a new branch named `sprint21-day8-table-data-test` from `main`

**Objective:** Complete Table data capture; run all 16 Subcategory A models through pipeline.

**Prerequisites:**
- Read Day 7 implementation — understand current Table parsing capabilities
- Read `PATH_SYNTAX_ERROR_CATALOG.md` Section 2.1 — full list of 16 Subcategory A models

**Tasks to Complete (~3-4 hours):**

1. **Handle edge cases** (1-1.5h)
   - Dotted indices for multi-dimensional tables
   - Empty cells and default values
   - String element columns
   - Multiple tables in a single model

2. **Emitter: output Table data in MCP** (1h)
   - Ensure the emitter outputs Table data values in the generated MCP file
   - May need to emit as parameter assignment statements or inline data blocks

3. **Run all 16 Subcategory A models through full pipeline (PR4)** (1h)
   - Track which models now compile cleanly in GAMS
   - Track which have secondary errors (after Table data is present)
   - Record solve status for models that compile

4. **Fix secondary errors** (0.5-1h, if time)
   - Some Subcategory A models may have additional errors once Table data is present
   - Fix the most straightforward ones; document the rest

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Table data parsing handles edge cases
- [ ] ≥10/16 Subcategory A models compile cleanly in GAMS
- [ ] path_syntax_error reduced by ≥10 models
- [ ] All 16 models tested through full pipeline (PR4)
- [ ] Mark Day 8 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run all 16 Subcategory A models through full pipeline and record results (PR4)

---

## Day 9 Prompt: WS6 — Match Rate Improvement

**Branch:** Create a new branch named `sprint21-day9-match-improvement` from `main`

**Objective:** Improve match rate via tolerance adjustment (port) and IndexOffset gradient fix (chakra, catmix, abel, qabel).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/SOLVE_MATCH_GAP_ANALYSIS.md` — per-model analysis
- Read `scripts/gamslib/test_solve.py` — find tolerance comparison logic
- Read `src/ad/derivative_rules.py` — find `_diff_varref()` and IndexOffset handling

**Tasks to Complete (~4-5 hours):**

1. **Tolerance adjustment for port** (<0.5h)
   - Relax comparison tolerance to match port (rel_diff 0.134%)
   - Options: increase rtol to 1e-2 or implement model-specific tolerance
   - Verify port now matches

2. **Fix IndexOffset gradient in `_diff_varref()`** (2-3h)
   - The differentiation engine compares `IndexOffset("t", Const(-1))` against concrete index strings like `"0"` — these never match
   - Fix to resolve IndexOffset indices against concrete set elements during differentiation
   - Test with chakra: `sum(t, dis(t-1)*c(t-1)^(1-eta))` should produce correct gradient

3. **Unit tests** (0.5h)
   - Test differentiation of expression with IndexOffset variable reference
   - Test that gradient is non-zero for lagged/lead variables
   - ≥3 new tests

4. **Re-run match candidates** (0.5h)
   - Run chakra, catmix, abel, qabel through pipeline — check if match improves
   - Run port — confirm match

5. **Investigate LP bound multipliers** (1h)
   - For apl1p, apl1pca, sparta, aircraft: check if KKT stationarity correctly handles parameter-assigned bounds
   - Document findings for future work if not immediately fixable

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] port matches (tolerance adjustment)
- [ ] IndexOffset gradient fix implemented
- [ ] chakra tested (may or may not match — document result)
- [ ] LP bound investigation documented
- [ ] ≥3 new unit tests
- [ ] Mark Day 9 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

## Day 10 Prompt: CHECKPOINT 2 + WS5 Deferred Issues (#789, #828)

**Branch:** Create a new branch named `sprint21-day10-checkpoint2-deferred` from `main`

**Objective:** Run Checkpoint 2 with full error category breakdown; fix #789 (min/max reformulation) and #828 (ibm1 bound multipliers).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` Sections 2.13 (#789) and 2.8 (#828)
- Read `docs/issues/ISSUE_789_minmax-reformulation-spurious-variables.md`
- Read `docs/issues/ISSUE_828_ibm1-locally-infeasible-stationarity.md`
- Read `src/kkt/reformulation.py` — find epigraph reformulation logic

**Tasks to Complete (~5 hours):**

1. **CHECKPOINT 2: Full pipeline retest (PR3 + PR5)** (1h)
   - Run: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record in SPRINT_LOG.md:
     - Parse: expect ≥141/160
     - Parse error breakdown (PR5): all parse-stage categories
     - Solve error breakdown (PR5): all solve-stage categories
     - Solve count: expect ≥36
     - Match count: expect ≥18
   - Verify all newly-parsing models from Days 1-8 have been tested through solve (PR4)

2. **Fix #789: min/max in objective equations** (2-2.5h)
   - Detect when min/max defines the objective variable
   - Use direct constraints (`z ≤ x, z ≤ y` for `z = min(x,y)`) instead of epigraph reformulation
   - Keep existing epigraph reformulation for non-objective cases
   - Test with affected models

3. **Fix #828: ibm1 bound multipliers** (1.5-2h)
   - Investigate nonzero cost constants in stationarity equations (-0.03, -0.08, -0.17)
   - Check if parameter-assigned bounds (`x.up(s) = sup(s,"inventory")`) are correctly resolved during KKT generation
   - Fix bound resolution; verify ibm1 solve status

4. **Unit tests** (0.5h)
   - Test objective-defining min/max reformulation
   - Test parameter-assigned bound resolution in KKT
   - ≥3 new tests

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Checkpoint 2 metrics recorded with full error category breakdown (PR5)
- [ ] Pipeline retest used `parse_model_file()` + `validate_model_structure()` (PR3)
- [ ] All newly-parsing models tested through solve (PR4)
- [ ] #789 min/max reformulation fix implemented and tested
- [ ] #828 ibm1 investigated (fix or document remaining issues)
- [ ] ≥3 new unit tests
- [ ] Mark Day 10 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md with Checkpoint 2 metrics
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record Checkpoint 2 metrics with error category breakdown in SPRINT_LOG.md (PR5)

---

## Day 11 Prompt: WS5 (#826) + WS3 Remaining + WS7 Emerging Blockers

**Branch:** Create a new branch named `sprint21-day11-decomp-emerging` from `main`

**Objective:** Fix decomp empty stationarity (#826); fix remaining internal_error models (indus, clearlak); triage and fix emerging translation blockers.

**Prerequisites:**
- Read `docs/issues/ISSUE_826_decomp-empty-stationarity-equation.md`
- Read `INTERNAL_ERROR_CATALOG.md` Sections 2.3 (indus) and 2.1 (clearlak)
- Review pipeline results from Checkpoint 2 — identify newly-parsing models with translation failures

**Tasks to Complete (~4-5 hours):**

1. **Fix #826: decomp empty stationarity** (1.5-2h)
   - Variable `lam(ss)` declared over full set but equations access via dynamic subset `s(ss)`
   - Detect empty stationarity equations post-generation
   - Eliminate or add penalty term
   - Verify decomp solve status

2. **Fix indus variable index arity** (1-1.5h)
   - Make `_make_symbol()` more lenient for index arity mismatches
   - Treat extra indices as warning rather than hard error
   - Verify indus parses

3. **Resolve clearlak** (0.5h)
   - Reclassify as `missing_include` (model depends on external `scenred.gms`)
   - OR implement auto-declare-on-first-assignment for undefined parameters
   - Document decision

4. **Triage emerging translation blockers** (1-1.5h)
   - Identify newly-parsing models (from WS1, WS2, WS3) that hit translation failures
   - Categorize failures
   - Fix the most straightforward blocker if time permits

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] decomp solve attempted (may still fail — document result)
- [ ] indus parses
- [ ] clearlak resolved (fixed or reclassified)
- [ ] internal_error ≤ 1
- [ ] Emerging translation blockers documented
- [ ] Mark Day 11 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run indus, clearlak, decomp through full pipeline and record results (PR4)

---

## Day 12 Prompt: WS8 — PATH Convergence Investigation

**Branch:** Create a new branch named `sprint21-day12-path-convergence` from `main`

**Objective:** Systematically analyze the 29 path_solve_terminated models. Classify root causes and document findings.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md` Section 5 — list of 29 path_solve_terminated models
- Read `SOLVE_MATCH_GAP_ANALYSIS.md` — methodology for analyzing solver output

**Tasks to Complete (~4-5 hours):**

1. **For each path_solve_terminated model** (3-4h):
   - Examine PATH solver output (iteration count, final residual, solver status)
   - Check complementarity residuals at termination
   - Test with relaxed tolerances (`convergence_tolerance = 1e-4`)
   - Test with increased iteration limit (`major_iteration_limit = 2000`)
   - Record: model name, iterations, residual, sensitivity to relaxation

2. **Classify each model** (0.5h):
   - **KKT correctness issue:** stationarity equations are wrong (gradient bugs, missing terms)
   - **Starting point sensitivity:** converges with better initialization
   - **Inherent difficulty:** nonconvex, degenerate, or ill-conditioned
   - **PATH options:** converges with different solver settings

3. **Write PATH_CONVERGENCE_ANALYSIS.md** (0.5h):
   - Per-model classification table
   - Recommended actions for each class
   - Priority fixes for Sprint 21 vs Sprint 22

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md` — per-model analysis
- ≥20/29 models classified

**This is primarily an analysis/documentation task — skip quality checks unless code changes are made.**

**Completion Criteria:**
- [ ] ≥20/29 path_solve_terminated models classified
- [ ] PATH_CONVERGENCE_ANALYSIS.md created
- [ ] Mark Day 12 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

## Day 13 Prompt: WS8 Completion + WS9 Solution Comparison Enhancement

**Branch:** Create a new branch named `sprint21-day13-path-solcomp` from `main`

**Objective:** Complete PATH convergence classification; implement primal/dual variable comparison in solution comparison framework.

**Prerequisites:**
- Read Day 12 PATH_CONVERGENCE_ANALYSIS.md — continue where Day 12 left off
- Read `scripts/gamslib/test_solve.py` — understand current comparison logic

**Tasks to Complete (~4-5 hours):**

1. **Complete PATH convergence classification** (1-2h)
   - Finish any remaining models from Day 12
   - Finalize PATH_CONVERGENCE_ANALYSIS.md
   - All 29 models classified

2. **Implement primal variable comparison** (1-1.5h)
   - Compare individual variable values between NLP and MCP solutions
   - Report max absolute and relative differences per variable
   - Flag variables with significant divergence

3. **Implement dual variable comparison** (1h)
   - Compare multiplier values (equation marginals)
   - Identify equations with large dual value differences

4. **Implement combined tolerance framework** (0.5h)
   - Combined relative/absolute tolerance: `|a-b| ≤ atol + rtol * max(|a|, |b|)`
   - Model-appropriate defaults

5. **Unit tests** (0.5h)
   - Test primal comparison with known values
   - Test dual comparison
   - Test combined tolerance logic
   - ≥3 new tests

**Quality Checks (if code changes):**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All 29 path_solve_terminated models classified in PATH_CONVERGENCE_ANALYSIS.md
- [ ] Primal variable comparison implemented
- [ ] Dual variable comparison implemented
- [ ] Combined tolerance framework implemented
- [ ] ≥3 new unit tests
- [ ] Mark Day 13 as complete in PLAN.md
- [ ] Update SPRINT_LOG.md
- [ ] Log progress to CHANGELOG.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

## Day 14 Prompt: FINAL CHECKPOINT + Sprint Close + Retrospective

**Branch:** Create a new branch named `sprint21-day14-sprint-close` from `main`

**Objective:** Run final pipeline retest; verify all acceptance criteria; complete solution comparison enhancement; write sprint retrospective.

**Prerequisites:**
- Read PLAN.md acceptance criteria table
- Read SPRINT_LOG.md — review progress across all days

**Tasks to Complete (~2-3 hours):**

1. **FINAL CHECKPOINT: Full pipeline retest (PR3 + PR5)** (1h)
   - Run: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record ALL metrics in SPRINT_LOG.md:
     - Parse: ≥ 135/160 ✓/✗
     - lexer_invalid_char: ≤ 5 ✓/✗
     - internal_error: ≤ 3 ✓/✗
     - Solve: ≥ 36 ✓/✗
     - Match: ≥ 20 ✓/✗
   - Full error category breakdown (PR5):
     - Parse-stage: lexer_invalid_char, internal_error, semantic_undefined_symbol, parser_invalid_expression, model_no_objective_def
     - Solve-stage: path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license
   - Test suite: `make test` — count and status
   - PATH analysis: all 29 models classified ✓/✗
   - Solution comparison: framework extended ✓/✗

2. **Complete solution comparison** (0.5-1h, if not finished on Day 13)
   - Complementarity residual comparison
   - Generate detailed mismatch reports

3. **Write Sprint Retrospective** (0.5-1h)
   - `docs/planning/EPIC_4/SPRINT_21/SPRINT_RETROSPECTIVE.md`
   - What went well / what could be improved / what we'd do differently
   - Sprint 22 recommendations
   - Process recommendation review (were PR2-PR5 effective?)
   - Final metrics comparison (baseline → final)

4. **Update PROJECT_PLAN.md** (0.25h)
   - Record Sprint 21 final metrics
   - Note any items deferred to Sprint 22

**This is primarily a documentation/analysis task. Run quality checks only if code changes are made.**

**Completion Criteria:**
- [ ] Final pipeline retest complete with full error category breakdown (PR3, PR5)
- [ ] All acceptance criteria verified (pass/fail for each)
- [ ] Solution comparison framework complete
- [ ] Sprint retrospective written
- [ ] PROJECT_PLAN.md updated with final metrics
- [ ] SPRINT_LOG.md finalized
- [ ] CHANGELOG.md updated
- [ ] Mark Day 14 as complete in PLAN.md

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record final metrics with full error category breakdown in SPRINT_LOG.md (PR5)

---

## Quick Reference: Branch Naming

| Day | Branch Name |
|-----|-------------|
| 0 | `sprint21-day0-kickoff` |
| 1 | `sprint21-day1-semantic-errors` |
| 2 | `sprint21-day2-macro-expansion` |
| 3 | `sprint21-day3-macro-eval` |
| 4 | `sprint21-day4-leadlag-params` |
| 5 | `sprint21-day5-checkpoint1-internal-error` |
| 6 | `sprint21-day6-emitter-fixes` |
| 7 | `sprint21-day7-table-data` |
| 8 | `sprint21-day8-table-data-test` |
| 9 | `sprint21-day9-match-improvement` |
| 10 | `sprint21-day10-checkpoint2-deferred` |
| 11 | `sprint21-day11-decomp-emerging` |
| 12 | `sprint21-day12-path-convergence` |
| 13 | `sprint21-day13-path-solcomp` |
| 14 | `sprint21-day14-sprint-close` |

---

## Quick Reference: Process Compliance Checklist

Every day's PR must include:
- [ ] **PR2:** PR number recorded in SPRINT_LOG.md
- [ ] **PR4:** (if parse improvements) Newly-parsing models tested through full pipeline

Every checkpoint must include:
- [ ] **PR3:** Pipeline retest via `parse_model_file()` + `validate_model_structure()`
- [ ] **PR5:** Error category breakdown (parse-stage + solve-stage)
