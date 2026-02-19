# Sprint 20 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 20 (Days 0–14). Each prompt is designed to be used when starting work on that specific day.

**Sprint Duration:** 15 days (Day 0 – Day 14)  
**Estimated Effort:** ~35–42 hours (~2.3–2.8h/day effective capacity)  
**Baseline:** parse 112/160 (70.0%), solve 27/96 (28.1%), match 10/27 (37.0%), lexer_invalid_char 26  

---

## Day 0 Prompt: Baseline Confirm + Sprint Kickoff

**Branch:** Create a new branch named `sprint20-day0-kickoff` from `main`

**Objective:** Verify clean baseline, internalize the plan, confirm all tests pass, initialize sprint log, update any stale KNOWN_UNKNOWNS.md entries.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (lines 1–50) — sprint overview, targets, and workstream summaries
- Read `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md` — exact baseline numbers at commit `dc390373`
- Read `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` — note items still marked INCOMPLETE (Unknowns 4.1, 5.x, 7.x)
- Review open GitHub issues referenced in PLAN.md (issues #753, #757, #763, #764, #789)

**Tasks to Complete (~1 hour):**

1. **Verify baseline** (0.25h)
   - Run `make test` — must show exactly 3,579 passed, 0 failed
   - Run `git log --oneline -5` — confirm you are on a clean commit from `main`

2. **Create SPRINT_LOG.md** (0.25h)
   - Create `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md`
   - Record baseline metrics (parse 112/160, translate 96/112, solve 27/96, match 10/27, lexer_invalid_char 26, tests 3,579)
   - Note the baseline commit: `dc390373`

3. **Update KNOWN_UNKNOWNS.md stale entries** (0.25h)
   - Unknowns 4.1, 5.x, 7.x are INCOMPLETE but were resolved by Tasks 3, 6, and 5 during prep
   - Update each to ✅ VERIFIED with a brief note pointing to the relevant design doc
   - Reference: `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md`, `LEXER_ERROR_CATALOG_UPDATE.md`, `TRANSLATE_ERROR_AUDIT.md`

4. **Map open issues to workstreams** (0.25h)
   - Review GitHub issues: `gh issue list --state open`
   - Note which issues correspond to WS1–WS6
   - Record in SPRINT_LOG.md

**Deliverables:**
- `make test` passing (3,579 tests)
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md` initialized with baseline metrics
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` updated (Unknowns 4.1, 5.x, 7.x → ✅ VERIFIED)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (3,579 tests)
  - [ ] `SPRINT_LOG.md` created with baseline metrics
  - [ ] KNOWN_UNKNOWNS.md Unknowns 4.1, 5.x, 7.x marked ✅ VERIFIED
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 0: Baseline Confirm + Sprint Kickoff" \
                --body "Completes Day 0 tasks from Sprint 20 PLAN.md: baseline verified, SPRINT_LOG.md created, KNOWN_UNKNOWNS.md stale entries resolved." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to each comment directly using `gh api "repos/jeffreyhorn/nlp2mcp/pulls/NNN/comments/$id/replies" -X POST -f body="..."`
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (lines 1–80, Day 0 schedule)
- `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`

---

## Day 1 Prompt: WS1 — `.l` Emission (IR + Parser)

**Branch:** Create a new branch named `sprint20-day1-l-emission-ir-parser` from `main`

**Objective:** Add `l_expr`/`l_expr_map` fields to `VariableDef` in the IR and modify the parser to store `.l` expressions instead of dropping them at `_handle_assign`.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md` — full design spec for `.l` IR + parser + emitter changes
- Read `src/ir/symbols.py` — understand current `VariableDef` structure
- Read `src/ir/parser.py` — find `_handle_assign` method; understand how `.l` assignments are currently dropped
- Review `data/gamslib/raw/circle.gms` if available — identify `a.l`, `b.l`, `r.l` initialization expressions

**Tasks to Complete (~3–3.5 hours):**

1. **Add `l_expr`/`l_expr_map` fields to `VariableDef`** (0.5h)
   - In `src/ir/symbols.py`, add `l_expr: Optional[Expr] = None` and `l_expr_map: Optional[Dict[str, Expr]] = None` to `VariableDef`
   - `l_expr` for scalar `.l` assignments; `l_expr_map` for indexed `.l` assignments (key = index domain string)

2. **Modify `_handle_assign` to store `.l` expressions** (1h)
   - In `src/ir/parser.py`, find the `_handle_assign` method (currently drops `.l` assignments)
   - Instead of dropping, parse the RHS expression and store it in `var_def.l_expr` (scalar) or `var_def.l_expr_map` (indexed)
   - Preserve existing behavior for `.fx`, `.lo`, `.up` assignments

3. **Unit tests: expression `.l` capture** (1h)
   - In `tests/unit/ir/`, add tests covering:
     - Scalar `.l` assignment: `a.l = 1.0;` → `var_def.l_expr` contains the expression
     - Indexed `.l` assignment: `x.l(i) = data(i);` → `var_def.l_expr_map` contains mapping
     - Chained `.l` assignment referencing another variable: `b.l = a.l + 1;`
   - Minimum 3 tests

4. **Verify circle IR captures `.l` expressions** (0.5h)
   - Run: `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; ir = parse_file('data/gamslib/raw/circle.gms'); print([v for v in ir.variables if v.l_expr is not None])"`
   - Expected: `a`, `b`, `r` variables have `l_expr` populated

**Deliverables:**
- `src/ir/symbols.py` — `VariableDef` has `l_expr`/`l_expr_map` fields
- `src/ir/parser.py` — `_handle_assign` stores `.l` expressions
- `tests/unit/ir/` — ≥ 3 new unit tests passing

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `circle.gms` IR contains `a.l_expr`, `b.l_expr`, `r.l_expr`
  - [ ] ≥ 3 unit tests covering scalar, indexed, and chained `.l` capture
  - [ ] All 3,579 + new tests pass
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 1: WS1 .l emission — IR + Parser" \
                --body "Completes Day 1 tasks from Sprint 20 PLAN.md: VariableDef l_expr/l_expr_map fields added, _handle_assign stores .l expressions, unit tests added." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 1 section, WS1 table)
- `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md`
- `src/ir/symbols.py`, `src/ir/parser.py`

---

## Day 2 Prompt: WS1 — `.l` Emission (Emitter + End-to-End)

**Branch:** Create a new branch named `sprint20-day2-l-emission-emitter` from `main`

**Objective:** Emit `.l` initialization expressions in the MCP GAMS output; validate circle solves via PATH and abel/chakra objective values match reference.

**Prerequisites:**
- Day 1 PR must be merged before starting Day 2 (Day 2 depends on `l_expr`/`l_expr_map` fields)
- Read `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md` — emitter section
- Read `src/emit/emit_gams.py` — find initialization section; understand where `.l` lines should be emitted
- Review `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` — circle/abel/chakra expected behavior

**Tasks to Complete (~2–2.5 hours):**

1. **Emit `l_expr`/`l_expr_map` in initialization section** (0.5h)
   - In `src/emit/emit_gams.py`, find the initialization section (after variable declarations, before solve)
   - For each `VariableDef` with `l_expr` set: emit `varname.l = <expr>;`
   - For each `VariableDef` with `l_expr_map` set: emit `varname.l(domain) = <expr>;` for each entry

2. **End-to-end circle test** (0.5h)
   - Run circle through the full pipeline: `python -m src.cli data/gamslib/raw/circle.gms`
   - Verify the MCP output contains `.l = ...` initialization lines for `a`, `b`, `r`
   - Check PATH converges: look for `model_status = 1` in solve output

3. **Verify circle PATH solve** (0.5h)
   - Confirm PATH solver returns `model_status = 1` (locally optimal/solved)
   - If PATH still fails: follow Contingency 3 (file issue, close #753, do not spend > 1h debugging)

4. **Check abel, chakra objective match** (0.5h)
   - Run abel and chakra through pipeline
   - Compare objective values against `gamslib_status.json` reference
   - Confirm both match within rtol

**Deliverables:**
- `src/emit/emit_gams.py` — emits `.l = <expr>` lines in initialization section
- circle MCP output has correct `.l` initialization
- PATH converges for circle (model_status=1); if not, issue filed and #753 closed
- abel, chakra objective values match reference

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] circle solves (PATH model_status=1), OR Contingency 3 executed and #753 closed
  - [ ] abel and chakra objective values match reference
  - [ ] All tests pass (≥ 3,579 + Day 1 new tests)
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 2: WS1 .l emission — Emitter + End-to-End" \
                --body "Completes Day 2 tasks from Sprint 20 PLAN.md: emitter emits .l initialization, circle/abel/chakra validated." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 2 section, WS1 emitter table)
- `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md`
- `src/emit/emit_gams.py`

---

## Day 3 Prompt: WS2 — IndexOffset `to_gams_string()` Extensions

**Branch:** Create a new branch named `sprint20-day3-indexoffset-to-gams-string` from `main`

**Objective:** Extend `IndexOffset.to_gams_string()` in `src/ir/ast.py` to handle `Unary("-", Call(...))` (sparta/tabora) and `Binary(op, Call, Call)` (otpop); verify mine/pindyck parse as cascading bonus.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md` — exact gap analysis for sparta/tabora/otpop; IndexOffset node types per model
- Read `src/ir/ast.py` — find `IndexOffset.to_gams_string()` method; understand current handled cases
- If available, smoke-test: `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/sparta.gms')"` to confirm current failure mode

**Tasks to Complete (~2.5–3 hours):**

1. **Extend `to_gams_string()` for `Unary("-", Call(...))` pattern** (1h)
   - In `src/ir/ast.py`, in `IndexOffset.to_gams_string()`, add handling for `Unary` node wrapping a `Call`
   - Pattern: `- ord(i)` → `"-ord(i)"`; `-floor(x)` → `"-floor(x)"`
   - Covers sparta and tabora

2. **Extend `to_gams_string()` for `Binary(op, Call, Call)` pattern** (1h)
   - Add handling for `Binary` node where both operands are `Call` nodes
   - Pattern: `ord(i) - ord(j)` → `"ord(i)-ord(j)"`
   - Covers otpop

3. **Unit tests for new `to_gams_string()` cases** (0.5h)
   - Add ≥ 4 unit tests in `tests/unit/ir/`:
     - `Unary("-", Call("ord", [i]))` → `"-ord(i)"`
     - `Unary("-", Call("floor", [x]))` → `"-floor(x)"`
     - `Binary("-", Call("ord", [i]), Call("ord", [j]))` → `"ord(i)-ord(j)"`
     - Combined nesting case

4. **Fix xfail sum-collapse for IndexOffset wrt-index** (0.5h)
   - Find the xfail test in `tests/` related to sum-collapse / IndexOffset wrt-index
   - If the fix is trivial (≤ 15 min): fix and turn xfail → pass
   - If non-trivial: document in the test why it remains xfail; update the `reason=` string

5. **Verify sparta, tabora, otpop translate; mine, pindyck parse** (0.5h)
   - Run each model through pipeline
   - Confirm sparta, tabora, otpop reach translate step without IndexOffset error
   - Confirm mine, pindyck now parse (D cascading resolved by IndexOffset fix)

**Deliverables:**
- `src/ir/ast.py` — `IndexOffset.to_gams_string()` handles Unary+Call and Binary+Call/Call
- `tests/unit/ir/` — ≥ 4 new unit tests
- sparta, tabora, otpop translate successfully
- mine, pindyck parse

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] sparta, tabora, otpop all translate without IndexOffset error
  - [ ] mine, pindyck parse
  - [ ] ≥ 4 unit tests pass
  - [ ] xfail addressed (fixed or documented)
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 3: WS2 IndexOffset to_gams_string() extensions" \
                --body "Completes Day 3 tasks from Sprint 20 PLAN.md: IndexOffset.to_gams_string() extended for Unary+Call and Binary+Call/Call; sparta/tabora/otpop translate; mine/pindyck parse." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 3 section, WS2 table)
- `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md`
- `src/ir/ast.py`

---

## Day 4 Prompt: WS3 Phase 1 — Lexer Quick Wins (Subcategories L + M + H)

**Branch:** Create a new branch named `sprint20-day4-lexer-phase1-lmh` from `main`

**Objective:** Fix lexer grammar for Subcategories L (Set-Model Exclusion), M (File/Acronym declarations), and H (Control Flow), targeting 9–10 new parse successes and cascading unblocks.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` — full analysis of subcategories L, M, H with exact token patterns and affected models
- Read `src/gams/gams_grammar.lark` — understand current grammar structure; find relevant rules
- Smoke-test current failures:
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/camcge.gms')"` (Subcat L)
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/senstran.gms')"` (Subcat M)
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/iobalance.gms')"` (Subcat H)

**Tasks to Complete (~3–4 hours):**

1. **Subcat L: `all - setname` pattern + dotted model-attribute** (1–2h)
   - Grammar: add support for `all - setname` in set expressions
   - Grammar: add support for dotted model attributes (e.g., `m.modelstat`)
   - Models: camcge, ferts, tfordy, cesam, spatequ

2. **Subcat M: `File` and `Acronym` declarations** (1h)
   - Grammar: stub `File declaration` and `Acronym declaration` as recognized-but-ignored statements
   - Models: senstran, worst

3. **Subcat H: `repeat/until` loop + `abort$` conditional** (1h)
   - Grammar: add `repeat ... until condition;` loop construct
   - Grammar: add `abort$(condition) "message"` statement
   - Models: iobalance (repeat/until), lop (abort$)
   - Cascading: fixes B-category error in nemhaus (blocked by H) and fdesign

4. **Unit tests for new grammar rules** (0.5h)
   - ≥ 3 unit tests covering: `all - setname`, File/Acronym stub, `repeat/until` or `abort$`

5. **Verify parse success on target models** (0.5h)
   - Smoke-test: camcge, cesam, ferts, tfordy, spatequ, senstran, worst, iobalance, lop
   - Also check: nemhaus (should now cascade-resolve)

**Deliverables:**
- `src/gams/gams_grammar.lark` — L/M/H patterns added
- `tests/unit/` — ≥ 3 new unit tests
- camcge, cesam, ferts, tfordy, spatequ, senstran, worst, iobalance, lop all parse
- nemhaus (B cascading) also parses

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] camcge, cesam, ferts, tfordy, spatequ parse (Subcat L — 5 models)
  - [ ] senstran, worst parse (Subcat M — 2 models)
  - [ ] iobalance, lop parse (Subcat H — 2 models)
  - [ ] nemhaus parse (B cascading — 1 model)
  - [ ] ≥ 3 unit tests pass
  - [ ] All existing 112 parse successes maintained (no regression)
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 4: WS3 Lexer Phase 1 — Subcategories L, M, H" \
                --body "Completes Day 4 tasks from Sprint 20 PLAN.md: lexer quick wins for Set-Model Exclusion (L), File/Acronym declarations (M), and Control Flow (H). 9–10 new parse successes." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 4 section, WS3 Phase 1 tables)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md`
- `src/gams/gams_grammar.lark`

---

## Day 5 Prompt: WS4 — model_no_objective_def Preprocessor Fix

**Branch:** Create a new branch named `sprint20-day5-model-no-objective-def-fix` from `main`

**Objective:** Fix `process_conditionals` in `src/ir/preprocessor.py` to handle same-line `$if` guard (the `$if set workSpace` bug), unblocking ≥ 10 of 13 affected models.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md` — full analysis of `$if set workSpace` preprocessor bug; exact reproduction cases; the 13 affected models
- Read `src/ir/preprocessor.py` — find `process_conditionals`; understand current behavior; identify where single-line `$if` handling is missing
- Smoke-test a known failing model:
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/camshape.gms')"` — should show `model_no_objective_def` or related error

**Tasks to Complete (~3 hours):**

1. **Fix `process_conditionals` for single-line `$if` guard** (1.5h)
   - In `src/ir/preprocessor.py`, in `process_conditionals`:
     - Current behavior: `$if set X` on its own line gates the next line
     - Bug: `$if set X stmt` (same line) is not handled — stmt is always included or always excluded
     - Fix: detect when the `$if` guard and the guarded statement appear on the same line; apply correct conditional logic
   - The 13 affected models all use `$if set workSpace` followed by a `model` or `solve` statement

2. **Unit tests: inline `$if` patterns** (0.5h)
   - Add ≥ 5 unit tests in `tests/unit/ir/`:
     - `$if set X stmt` included when X is set
     - `$if set X stmt` excluded when X is not set
     - `$if not set X stmt` (negated form)
     - Multi-statement same-line guard (if applicable)
     - Nested: `$if set X $if set Y stmt`

3. **End-to-end: verify ≥ 10 of 13 `$if`-bug models now parse** (0.5h)
   - Run: camshape, catmix, chain, lnts, polygon, and others from the 13-model list
   - Confirm each reaches parse stage without `model_no_objective_def`

4. **Handle robot typo (`miniziming`) if needed** (0.25h)
   - Check if robot.gms fails due to the typo vs. the `$if` bug
   - If typo-only: add a grammar alias or preprocessor normalization

5. **Document lmp2 doubly-nested loop** (0.25h)
   - Confirm lmp2 fails due to a different reason (doubly-nested loop, not `$if` bug)
   - File a GitHub issue for lmp2 if one doesn't exist
   - Note in SPRINT_LOG.md that lmp2 is deferred to Sprint 21

**Deliverables:**
- `src/ir/preprocessor.py` — `process_conditionals` handles inline `$if` guard
- `tests/unit/ir/` — ≥ 5 unit tests for inline `$if` variants
- model_no_objective_def count ≤ 4
- ≥ 10 of 13 `$if`-bug models now parse
- lmp2 issue filed (if not already open)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] model_no_objective_def ≤ 4 (down from 14)
  - [ ] ≥ 10 of 13 `$if`-bug models newly parse
  - [ ] ≥ 5 unit tests for inline `$if` patterns pass
  - [ ] lmp2 documented and issue filed
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 5: WS4 model_no_objective_def preprocessor fix" \
                --body "Completes Day 5 tasks from Sprint 20 PLAN.md: process_conditionals inline \$if fix; model_no_objective_def ≤ 4; ≥ 10 of 13 \$if-bug models now parse." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 5 section, WS4 table)
- `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md`
- `src/ir/preprocessor.py`

---

## Day 6 Prompt: Checkpoint 1 + Buffer

**Branch:** Create a new branch named `sprint20-day6-checkpoint1` from `main`

**Objective:** Evaluate Checkpoint 1 GO/NO-GO criteria; use buffer to address any Day 1–5 overruns; do NOT start new workstreams until checkpoint passes.

**Prerequisites:**
- All Day 1–5 PRs merged (or in final review)
- Read `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Checkpoint 1 section) — exact GO/NO-GO criteria
- Run a partial pipeline retest to get current parse/solve numbers:
  ```bash
  .venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet
  ```

**Tasks to Complete (~1–2 hours for checkpoint eval; up to 3h total if buffer used):**

1. **Evaluate Checkpoint 1 criteria** (0.5h)
   Run the pipeline and check:
   - Parse success ≥ 125/160?
   - Solve success ≥ 28?
   - WS1 (`.l` emission) PR merged?
   - WS2 (IndexOffset) PR merged?
   - All tests passing?

2. **Decision: GO or NO-GO**
   - **If GO:** Record checkpoint results in SPRINT_LOG.md; proceed per the Day 7–14 schedule
   - **If NO-GO (parse < 125):** Redirect buffer time to:
     - Debug which Subcat L/M/H models did not parse
     - Complete any WS1/WS2 work not merged
     - Do NOT start WS3 Phase 2 until parse ≥ 125 or the contingency plan is invoked
   - **If NO-GO (solve < 28):** Investigate circle/abel PATH failures; debug `.l` emission effect

3. **Buffer work (if GO)** (0–1.5h)
   - Address any Day 1–5 items that were deferred
   - Review and triage the GitHub issues filed during Days 3–5
   - Update SPRINT_LOG.md with checkpoint results

4. **Checkpoint 1 Contingency: invoke Contingency 1 if parse < 120** (if triggered)
   - Record: "Contingency 1 triggered" in SPRINT_LOG.md
   - Defer Subcategory A (WS3 Phase 2) to Sprint 21
   - Redirect Days 7–8 to WS5 pipeline match work and WS6 golden-file tests
   - Reduce parse target to ≥ 120/160

**Deliverables:**
- Checkpoint 1 evaluation recorded in SPRINT_LOG.md (with exact numbers)
- GO/NO-GO decision documented
- Any Day 1–5 overruns resolved (or contingency plan activated)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Checkpoint 1 GO/NO-GO criteria evaluated and recorded
- [ ] Parse ≥ 125/160 (GO) OR contingency plan documented (NO-GO)
- [ ] Solve ≥ 28 (GO) OR PATH debugging initiated (NO-GO)
- [ ] WS1 and WS2 PRs merged
- [ ] SPRINT_LOG.md updated with checkpoint metrics
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes (likely documentation only):
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 6: Checkpoint 1 Evaluation" \
                --body "Completes Day 6 tasks from Sprint 20 PLAN.md: Checkpoint 1 GO/NO-GO documented; SPRINT_LOG.md updated with checkpoint metrics." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 6 + Checkpoint 1 section, lines ~145–175)
- `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md`

---

## Day 7 Prompt: WS3 Phase 2 — Compound Set Data Part 1 (Subcategory A)

**Branch:** Create a new branch named `sprint20-day7-lexer-subcat-a-part1` from `main`

**Objective:** Extend Subcategory A compound set data grammar: multi-word set elements (mexls) and parenthesized sub-list in table header (sarf/indus).

**Prerequisites:**
- Checkpoint 1 must be GO (parse ≥ 125/160) before starting this day
- Read `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory A section) — exact patterns for mexls (multi-word elements) and sarf (parenthesized sub-lists)
- Smoke-test current failures:
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/mexls.gms')"` — multi-word set element error
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/sarf.gms')"` — parenthesized sub-list error

**Tasks to Complete (~3 hours):**

1. **Multi-word set elements (`wire rod`, `hot rolled`, etc.)** (1.5h)
   - Grammar: extend set element rules to allow quoted or space-joined multi-word labels in set/table definitions
   - This may require changes to both the grammar and the string handling in `src/ir/parser.py`
   - Target: mexls parses

2. **Parenthesized sub-list in table header (`(sch-1*sch-3)`)** (1h)
   - Grammar: allow `(range_expr)` in table column headers
   - May also require changes to set range handling
   - Target: sarf parses; indus may also resolve

3. **Unit tests** (0.5h)
   - ≥ 3 unit tests: multi-word element, parenthesized sub-list, combination

**Deliverables:**
- `src/gams/gams_grammar.lark` — multi-word elements and parenthesized sub-lists supported
- mexls, sarf parse; indus may also resolve
- ≥ 3 unit tests pass

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] mexls parses (multi-word set elements)
- [ ] sarf parses (parenthesized sub-list in table header)
- [ ] ≥ 3 unit tests pass
- [ ] All existing parse successes maintained (no regression)
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 7: WS3 Lexer Subcat A Part 1 — multi-word elements, parenthesized sub-lists" \
                --body "Completes Day 7 tasks from Sprint 20 PLAN.md: mexls and sarf now parse." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 7 section, WS3 Phase 2 Part 1)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory A)
- `src/gams/gams_grammar.lark`

---

## Day 8 Prompt: WS3 Phase 2 — Compound Set Data Part 2 + Inline Scalar Data (Subcats A + E)

**Branch:** Create a new branch named `sprint20-day8-lexer-subcat-a-part2-e` from `main`

**Objective:** Complete Subcategory A grammar (multi-line table row label continuation, hyphenated+numeric elements); fix Subcategory E (inline scalar data). Target: ≥ 6 of 9 models in scope now parse.

**Prerequisites:**
- Day 7 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory A Part 2 and Subcategory E sections) — paperco, turkpow, turkey, cesam2, gussrisk, trnspwl patterns
- Smoke-test:
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/paperco.gms')"` — multi-line table row label
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/cesam2.gms')"` — inline scalar data

**Tasks to Complete (~3–4 hours):**

1. **Multi-line table row label continuation (paperco pattern)** (1h)
   - Grammar: allow table row labels that span multiple lines (continuation via indentation or explicit marker)
   - Target: paperco parses

2. **Hyphenated+numeric element (`hydro-4.1978`) — turkpow/turkey pattern** (1h)
   - Grammar: extend identifier/element rules to allow `-` followed by a decimal number
   - This may interact with unary minus; handle carefully to avoid ambiguity
   - Target: turkpow, turkey parse

3. **Inline scalar data (`/ .05 /`, `/ 50 /`) — Subcategory E** (1h)
   - Grammar: add `scalar / value /` initialization form (currently only `scalar = value` is supported)
   - Target: cesam2, gussrisk, trnspwl parse

4. **Pipeline retest on all Subcat A + E target models** (0.5h)
   - Run smoke-tests on: indus, mexls, paperco, sarf, turkey, turkpow, cesam2, gussrisk, trnspwl
   - Document which of the 9 now parse; note any remaining blockers

5. **Unit tests** (0.5h)
   - ≥ 2 unit tests: hyphenated+numeric element, inline scalar data form

**Deliverables:**
- `src/gams/gams_grammar.lark` — multi-line table label, hyphenated+numeric, inline scalar data
- At least 6 of: indus, mexls, paperco, sarf, turkey, turkpow, cesam2, gussrisk, trnspwl now parse
- ≥ 2 additional unit tests

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] At least 6 of the 9 Subcat A+E models parse
  - [ ] No regression in previously-passing models
  - [ ] ≥ 2 new unit tests pass
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 8: WS3 Lexer Subcat A Part 2 + Subcat E" \
                --body "Completes Day 8 tasks from Sprint 20 PLAN.md: multi-line table labels (paperco), hyphenated+numeric elements (turkpow/turkey), inline scalar data (cesam2/gussrisk/trnspwl)." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 8 section, WS3 Phase 2 Part 2 + E)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory A Part 2 and E)
- `src/gams/gams_grammar.lark`

---

## Day 9 Prompt: WS5 Part A — Pipeline Match Tolerance Fix + Regression Tests

**Branch:** Create a new branch named `sprint20-day9-rtol-tolerance-match` from `main`

**Objective:** Raise `DEFAULT_RTOL` from `1e-6` to `1e-4` in the pipeline; verify the 5 near-match models now pass; add solve-level regression tests for matching models.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` — full analysis of near-match models (chem, dispatch, hhmax, mhw4d, mhw4dx) and the rtol sensitivity analysis
- Read `scripts/gamslib/test_solve.py` — find `DEFAULT_RTOL`; understand how it's used in objective comparison
- Review current match list: run `python scripts/gamslib/query_status.py --status match` (or similar) to confirm baseline 10 matches

**Tasks to Complete (~3 hours):**

1. **Raise `DEFAULT_RTOL` to `1e-4`** (0.5h)
   - In `scripts/gamslib/test_solve.py`, change `DEFAULT_RTOL = 1e-6` to `DEFAULT_RTOL = 1e-4`
   - Verify the change applies to all objective value comparisons

2. **Run full pipeline retest to confirm match count** (0.5h)
   - Run: `.venv/bin/python scripts/gamslib/run_full_test.py --only-solve --quiet`
   - Check: chem, dispatch, hhmax, mhw4d, mhw4dx now show as "match"
   - Confirm match ≥ 15

3. **Verify no false positives at new rtol** (0.5h)
   - Review any new "match" entries that are NOT in the expected +5 list
   - If unexpected new matches appear: investigate each to confirm the result is genuine (not a numeric coincidence)
   - Document findings in SPRINT_LOG.md

4. **Add solve-level regression tests (WS6 partial)** (1h)
   - In `tests/e2e/` (create `test_gamslib_match.py` if it doesn't exist):
     - Add regression tests for ≥ 5 of the models now matching
     - Each test: run full pipeline, assert objective value matches reference within rtol=1e-4
   - These tests guard against regressions in the models we've worked hard to match

5. **Update SPRINT_LOG.md** (0.25h)
   - Record new match count, list of newly-matching models

**Deliverables:**
- `scripts/gamslib/test_solve.py` — `DEFAULT_RTOL = 1e-4`
- Full pipeline match ≥ 15
- `tests/e2e/test_gamslib_match.py` (or equivalent) — ≥ 5 regression tests pass
- SPRINT_LOG.md updated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Full pipeline match ≥ 15
  - [ ] chem, dispatch, hhmax, mhw4d, mhw4dx all now match
  - [ ] No false positives (all new matches verified genuine)
  - [ ] ≥ 5 regression tests added and passing
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 9: WS5 rtol tolerance fix + regression tests" \
                --body "Completes Day 9 tasks from Sprint 20 PLAN.md: DEFAULT_RTOL raised to 1e-4; full pipeline match ≥ 15; ≥ 5 regression tests added." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 9 section, WS5 Part A)
- `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md`
- `scripts/gamslib/test_solve.py`

---

## Day 10 Prompt: WS5 Part B — Inf Parameter Handling + Model Validation Prep

**Branch:** Create a new branch named `sprint20-day10-inf-params-model-validation` from `main`

**Objective:** Fix `codegen_numerical_error` for ±Inf parameter values; begin model validation run on all parse-success models.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md` — section on `codegen_numerical_error` (decomp, gastrans, gtm, ibm1) and the ±Inf pattern
- Read `src/validation/numerical.py` — find `validate_parameter_values`; understand current handling
- Read `src/emit/emit_gams.py` — find where parameter bounds are emitted

**Tasks to Complete (~3 hours):**

1. **Fix `validate_parameter_values` for ±Inf values** (1h)
   - In `src/validation/numerical.py`, modify `validate_parameter_values` (or the relevant function) to treat IEEE `+inf` / `-inf` as valid "no bound" values rather than raising `codegen_numerical_error`
   - Do NOT silently drop the value — instead, pass it through to the emitter

2. **Emit `.up = +Inf` / `.lo = -Inf` as appropriate** (0.5h)
   - In `src/emit/emit_gams.py`, ensure that when a parameter value is `+inf`, it is emitted as `varname.up = +Inf` in GAMS syntax (not as a numeric literal)
   - Similarly for `-inf` → `varname.lo = -Inf`

3. **Unit tests** (0.5h)
   - ≥ 2 unit tests: ±Inf parameter value passes validation and is emitted as `+Inf`/`-Inf` in GAMS output

4. **End-to-end: decomp, gastrans, gtm, ibm1** (0.5h)
   - Run each through the pipeline
   - Confirm 0 `codegen_numerical_error` (except iswnm which has a timeout, not a numerical error)

5. **Begin model validation run** (0.5h)
   - Start a full pipeline retest in the background:
     ```bash
     .venv/bin/python scripts/gamslib/run_full_test.py --quiet > /tmp/sprint20_day10_retest.log 2>&1 &
     ```
   - This will run overnight and be checked on Day 11

**Deliverables:**
- `src/validation/numerical.py` — ±Inf values no longer raise `codegen_numerical_error`
- `src/emit/emit_gams.py` — ±Inf emitted as `+Inf`/`-Inf` in GAMS syntax
- ≥ 2 unit tests
- decomp, gastrans, gtm, ibm1 translate without error
- Full pipeline retest started (background)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] codegen_numerical_error ≤ 1 (iswnm timeout only)
  - [ ] decomp, gastrans, gtm, ibm1 translate without error
  - [ ] ≥ 2 unit tests pass
  - [ ] Full pipeline retest started
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 10: WS5 Inf parameter handling + model validation" \
                --body "Completes Day 10 tasks from Sprint 20 PLAN.md: ±Inf parameter values handled; codegen_numerical_error ≤ 1; model validation retest started." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 10 section, WS5 Part B)
- `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md`
- `src/validation/numerical.py`, `src/emit/emit_gams.py`

---

## Day 11 Prompt: Model Validation + Checkpoint 2

**Branch:** Create a new branch named `sprint20-day11-checkpoint2` from `main`

**Objective:** Complete model validation using Day 10's pipeline retest results; evaluate Checkpoint 2 GO/NO-GO criteria; triage any new issues; decide on Phase 3 (Days 12–13).

**Prerequisites:**
- Day 10 pipeline retest must be complete (check `/tmp/sprint20_day10_retest.log`)
- Read `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Checkpoint 2 section) — exact GO/NO-GO criteria
- Read `scripts/gamslib/gamslib_status.json` — updated results from Day 10 retest

**Tasks to Complete (~2–3 hours):**

1. **Read Day 10 pipeline retest results** (0.5h)
   - Query the results: `python -c "import json; d=json.load(open('scripts/gamslib/gamslib_status.json')); ..."`
   - Extract: parse count, lexer_invalid_char count, model_no_objective_def count, match count, solve count
   - Record in SPRINT_LOG.md

2. **Evaluate Checkpoint 2 criteria** (0.5h)
   - Parse success ≥ 125/160?
   - lexer_invalid_char ≤ 11?
   - model_no_objective_def ≤ 4?
   - Full pipeline match ≥ 15?
   - Solve success ≥ 30?
   - All tests passing?

3. **Triage new issues from validation** (0.5h)
   - Review any models that newly parse but fail at translate or solve
   - File GitHub issues for each new failure type discovered
   - Prioritize: can any be fixed before Day 14?

4. **Decision: GO or NO-GO for Phase 3**
   - **If GO:** Proceed with Phase 3 (Days 12–13: Subcat J/K, WS6 remaining)
   - **If NO-GO:** Redirect Days 12–13 to fix remaining Checkpoint 2 blockers

5. **Checkpoint 2 Contingency (if triggered)**
   - If lexer_invalid_char > 11: defer J/K (mathopt3, dinam) to Sprint 21; focus on remaining Subcat A/E models
   - If model_no_objective_def > 4: file detailed issue for remaining models; defer lmp2 fix to Sprint 21
   - If match < 15: check rtol application; verify abel/chakra `.l` emission is correct

**Deliverables:**
- SPRINT_LOG.md updated with Checkpoint 2 metrics
- Checkpoint 2 GO/NO-GO decision documented
- New issues filed for any validation-discovered failures
- Day 12–13 plan confirmed (Phase 3 or contingency)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Checkpoint 2 criteria evaluated and recorded
- [ ] Parse ≥ 125/160 OR contingency documented
- [ ] lexer_invalid_char ≤ 11 OR contingency documented
- [ ] model_no_objective_def ≤ 4 OR contingency documented
- [ ] Full pipeline match ≥ 15 OR investigation initiated
- [ ] Solve ≥ 30 OR investigation initiated
- [ ] SPRINT_LOG.md updated
- [ ] Mark Day 11 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Check off all Checkpoint 2 criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes (documentation only):
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 11: Checkpoint 2 Evaluation + Model Validation" \
                --body "Completes Day 11 tasks from Sprint 20 PLAN.md: Checkpoint 2 evaluated; SPRINT_LOG.md updated with validation results." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 11 + Checkpoint 2 section, lines ~205–240)
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md`
- `scripts/gamslib/gamslib_status.json`

---

## Day 12 Prompt: Phase 3 + WS6 — Subcat J/K Grammar + Regression Tests

**Branch:** Create a new branch named `sprint20-day12-phase3-regression-tests` from `main`

**Objective:** (If Checkpoint 2 GO) Add Phase 3 grammar for Subcategory J (square bracket function call) and K (miscellaneous); add WS6 golden-file regression tests for newly-matched models.

**Prerequisites:**
- Checkpoint 2 must be GO before starting Phase 3 grammar work
- Read `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory J and K sections) — mathopt3 square bracket pattern; dinam miscellaneous pattern
- Smoke-test:
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/mathopt3.gms')"` — square bracket function call
  - `python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/dinam.gms')"` — miscellaneous

**Tasks to Complete (~3 hours):**

1. **Phase 3: Square bracket function call (mathopt3) — Subcat J** (1h)
   - Grammar: add `funcname[args]` as an alternative to `funcname(args)` for function calls
   - mathopt3 uses `[ ]` instead of `( )` for certain function calls
   - Target: mathopt3 parses

2. **Phase 3: Miscellaneous (dinam) — Subcat K** (1h)
   - Investigate the exact error in dinam
   - Add the minimal grammar/preprocessor fix needed
   - Target: dinam parses (if tractable within 1h; if not, file issue and defer to Sprint 21)

3. **WS6: Golden-file solve regression tests for newly-matched models** (1h)
   - In `tests/e2e/test_gamslib_match.py` (or equivalent):
     - Add ≥ 3 additional regression tests for models that newly matched during Sprint 20
     - Each test should assert: parse succeeds, translate succeeds, objective value matches reference within rtol=1e-4
   - Total: bring WS6 coverage to ≥ 8 regression tests (5 from Day 9 + 3 new)

**Deliverables:**
- `src/gams/gams_grammar.lark` — Subcat J (square bracket call) and K (dinam fix) added
- mathopt3 parses; dinam parses (or issue filed for Sprint 21)
- ≥ 3 additional regression tests in `tests/e2e/`

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] mathopt3 parses (Subcat J)
- [ ] dinam parses OR issue filed for Sprint 21 (Subcat K)
- [ ] ≥ 3 additional regression tests added and passing
- [ ] Total WS6 coverage ≥ 8 solve-level regression tests
- [ ] Mark Day 12 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 12: Phase 3 grammar (Subcat J+K) + WS6 regression tests" \
                --body "Completes Day 12 tasks from Sprint 20 PLAN.md: mathopt3 (Subcat J), dinam (Subcat K), ≥ 3 additional regression tests." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 12 section, Phase 3 + WS6)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` (Subcategory J and K)
- `src/gams/gams_grammar.lark`

---

## Day 13 Prompt: Sprint Close Prep — Issues + Documentation

**Branch:** Create a new branch named `sprint20-day13-sprint-close-prep` from `main`

**Objective:** File/close all remaining issues; smoke-test every deferred item to confirm scope; update SPRINT_LOG.md; run final `make test`.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 13 section) — deferred items list
- Review `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` — any remaining open/partial entries
- Have the full list of deferred items ready:
  - Accounting variable detection (mexss/#764)
  - AD condition propagation (chenery/#763)
  - `.scale` emission
  - lmp2 doubly-nested loop
  - saras/springchain preprocessor issues
  - Any Subcat A/E/K models not fixed this sprint

**Tasks to Complete (~2 hours):**

1. **File issues for all deferred items** (0.75h)
   - For each deferred item, confirm a GitHub issue exists (or create one)
   - Issues should include: current failure mode, expected fix approach, estimated effort, sprint target (Sprint 21)
   - Use: `gh issue create --title "..." --body "..." --label "sprint-21"`

2. **Smoke-test all "not fixable" declarations** (0.75h)
   - For every item you are declaring as deferred, run:
     ```bash
     python -m src.cli data/gamslib/raw/<model>.gms 2>&1 | head -30
     ```
   - Confirm the failure mode is what you documented (do not defer something that might actually be fixed now)
   - This is the Sprint 19 lesson: always verify before declaring deferred

3. **Update SPRINT_LOG.md with final pre-close metrics** (0.25h)
   - Record all metrics from most recent pipeline retest
   - Note: "awaiting Day 14 final retest for official sprint close metrics"

4. **Run final `make test`** (0.25h)
   - Must pass 0 failures
   - Record test count in SPRINT_LOG.md

**Deliverables:**
- All deferred items have GitHub issues
- Each deferred item smoke-tested and failure mode confirmed
- SPRINT_LOG.md updated
- `make test` passing (0 failures)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All deferred items have GitHub issues with sprint-21 label
- [ ] All deferred items smoke-tested
- [ ] SPRINT_LOG.md updated with final pre-close metrics
- [ ] `make test` passes (0 failures)
- [ ] Mark Day 13 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes (documentation only):
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 13: Sprint close prep — issues + documentation" \
                --body "Completes Day 13 tasks from Sprint 20 PLAN.md: deferred items documented; smoke-tests verified; SPRINT_LOG.md updated." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 13 section)
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md`

---

## Day 14 Prompt: Sprint Close + Retrospective

**Branch:** Create a new branch named `sprint20-day14-sprint-close-retrospective` from `main`

**Objective:** Run the final full pipeline retest; record official sprint metrics vs. targets; write the Sprint 20 Retrospective; update CHANGELOG.md; tag release if appropriate.

**Prerequisites:**
- All Day 0–13 PRs merged
- Read `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Sprint-Level Acceptance Criteria section) — final targets
- Read `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md` — accumulated metrics
- Reference retrospective template from previous sprints (e.g., `docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md`)

**Tasks to Complete (~2–3 hours):**

1. **Final full pipeline retest** (1h)
   Run the full test suite and pipeline:
   ```bash
   make test
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
   Wait for completion (may take ~25 min). Extract final metrics:
   ```bash
   python -c "
   import json
   d = json.load(open('scripts/gamslib/gamslib_status.json'))
   parse_ok = sum(1 for v in d.values() if v.get('parse') == 'ok')
   # ... full query
   "
   ```

2. **Record final metrics vs. targets** (0.25h)
   Update `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md` with a final "Sprint Close" section:
   
   | Metric | Baseline | Target | Actual | Status |
   |---|---|---|---|---|
   | Parse success | 112/160 | ≥ 127/160 | X/160 | ✅/❌ |
   | lexer_invalid_char | 26 | ≤ 11 | X | ✅/❌ |
   | model_no_objective_def | 14 | ≤ 4 | X | ✅/❌ |
   | Translate success | 96/112 | ≥ 110/127 | X/Y | ✅/❌ |
   | Solve success | 27 | ≥ 30 | X | ✅/❌ |
   | Full pipeline match | 10 | ≥ 15 | X | ✅/❌ |
   | Tests | 3,579 | ≥ 3,650 | X | ✅/❌ |

3. **Write Sprint 20 Retrospective** (1h)
   Create `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` with sections:
   - **Sprint Summary**: final metrics vs. targets
   - **What Went Well**: workstreams that delivered on time/ahead
   - **What Didn't Go Well**: missed targets, overruns, surprises
   - **Process Improvements for Sprint 21**: 3–6 specific improvements
   - **Deferred Items**: full list with issue numbers
   - **Sprint 21 Priorities**: top 5 items based on sprint learnings

4. **Update CHANGELOG.md** (0.25h)
   - Add a Sprint 20 summary entry under `[Unreleased]`
   - Include: final parse/solve/match numbers, key workstreams completed

5. **Tag release (if appropriate)** (0.25h)
   - If sprint targets were met: `git tag sprint20-final -m "Sprint 20 complete: parse X/160, match X, solve X"`
   - Push tag: `git push origin sprint20-final`

**Deliverables:**
- Final `gamslib_status.json` with Sprint 20 results
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md` — final metrics table
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` — complete retrospective
- `CHANGELOG.md` — Sprint 20 summary entry
- Git tag (if targets met)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Final pipeline retest complete
  - [ ] Sprint metrics recorded vs. targets
  - [ ] SPRINT_RETROSPECTIVE.md written
  - [ ] CHANGELOG.md updated
  - [ ] Git tag created (if targets met)
- [ ] Mark Day 14 as complete in `docs/planning/EPIC_4/SPRINT_20/PLAN.md`
- [ ] Log final progress to `CHANGELOG.md`
- [ ] Check off all Sprint-Level Acceptance Criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 20 Day 14: Sprint Close + Retrospective" \
                --body "Completes Day 14 tasks from Sprint 20 PLAN.md: final pipeline retest, official sprint metrics recorded, SPRINT_RETROSPECTIVE.md written, CHANGELOG.md updated." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review, address all comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` (Day 14 section + Sprint-Level Acceptance Criteria)
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md`
- `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`
- Previous retrospective: `docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch from `main`
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant code change
   - Track progress against time estimates
   - If blocked, file an issue and continue with the next task (do not brute-force)

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update `PLAN.md`, and `CHANGELOG.md`
   - Update `SPRINT_LOG.md`
   - Create PR and request Copilot review
   - Address review comments — **reply directly to each comment** using:
     ```bash
     gh api "repos/jeffreyhorn/nlp2mcp/pulls/NNN/comments/$id/replies" -X POST -f body="Fixed in <hash>. <explanation>"
     ```
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

---

## Notes

- Each prompt is self-contained: prerequisites ensure all necessary context is available
- Branch naming: `sprint20-day[N]-[short-description]` — always lowercase kebab-case
- **PR comments**: ALWAYS reply to review comments directly (not just comment on the PR). Use `gh api "repos/jeffreyhorn/nlp2mcp/pulls/NNN/comments/$id/replies"`
- Checkpoint days (6 and 11) are GO/NO-GO gates — do not start new workstreams until checkpoint criteria are met
- Contingency plans are in `PLAN.md` — activate them explicitly and document the decision in SPRINT_LOG.md
- The `data/gamslib/raw/` directory is not in CI — always use `pytest.skip()` in fixtures that need `.gms` files when the file is absent
- Pipeline retest takes ~25 minutes — run it backgrounded when possible:
  ```bash
  .venv/bin/python scripts/gamslib/run_full_test.py --quiet > /tmp/sprint20_retest.log 2>&1 &
  ```
- All reference documents are in `docs/planning/EPIC_4/SPRINT_20/`
