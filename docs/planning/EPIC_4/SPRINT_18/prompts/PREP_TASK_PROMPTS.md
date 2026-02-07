# Sprint 18 Prep Task Prompts

**Purpose:** Self-contained prompts for executing Tasks 2-10 of the Sprint 18 Preparation Plan
**Reference:** `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`
**Known Unknowns:** `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`

---

## Task 2: Survey GAMSLIB Corpus for Syntax Error Indicators

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task2
```

### Objective

Survey the 160 convex GAMSLIB models to estimate how many have GAMS-level syntax errors, understand what types of errors exist, and scope the syntactic validation work for Sprint 18.

### Why This Matters

Sprint 18's syntactic validation component assumes some models in the corpus have GAMS-level syntax errors. Before building `test_syntax.py`, we need to understand the scope: Are there 2 models or 20? What kinds of errors exist? This survey informs time estimates and the syntax error report format.

### What Needs to Be Done

#### Step 1: Quick Compilation Test on Sample Models (1 hour)

Test `gams action=c` on a stratified sample:
- 5 models that parse successfully (should compile)
- 5 models with `lexer_invalid_char` (may or may not compile)
- 2 models with known issues (`camcge`, infeasible models)
- Record: exit code, .lst file content, error format

```bash
# Example test command
gams camcge.gms action=c > /dev/null 2>&1; echo $?
# Expected: non-zero exit code

gams himmel11.gms action=c > /dev/null 2>&1; echo $?
# Expected: 0 (compiles successfully)
```

#### Step 2: Cross-Reference Pipeline Failures (1 hour)

For each of the 99 models that fail to parse:
- Check if the failure might be a GAMS syntax error vs. an nlp2mcp limitation
- Look for patterns: models mentioning "syntax" in error messages
- Cross-reference with GAMSLIB documentation/changelogs if available

#### Step 3: Estimate Scope (30 min)

Document:
- Estimated number of models with GAMS syntax errors
- Types of syntax errors observed (mismatched parens, undefined symbols, etc.)
- Which errors are GAMS bugs vs. intentional GAMS features nlp2mcp doesn't support
- Impact on corpus denominator (e.g., if 10 models excluded, denominator drops from 160 to 150)

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` with survey results
- List of sample models tested and their GAMS compilation outcomes
- Estimated scope for `test_syntax.py` implementation

### Acceptance Criteria

- [ ] At least 12 models tested with `gams action=c` (stratified sample)
- [ ] GAMS exit code behavior documented for success and failure
- [ ] .lst file error format documented (for programmatic parsing)
- [ ] Estimated number of syntax-error models (range)
- [ ] Cross-reference with nlp2mcp pipeline failures complete
- [ ] Impact on corpus denominator estimated

### Verify Known Unknowns

This task verifies **Unknowns 1.1, 1.2, 1.3, 1.8** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 1.1** (Does `gams action=c` reliably detect all syntax errors?): Update with exit code findings, test results for clean vs. error models, and any false positive/negative observations
- **Unknown 1.2** (How many GAMSLIB models actually have GAMS syntax errors?): Update with the estimated count and confidence level from the survey
- **Unknown 1.3** (Can GAMS .lst file error messages be parsed programmatically?): Update with the observed .lst error format and parsing feasibility
- **Unknown 1.8** (What is the expected runtime for compiling all 160 models?): Update with timing data from the sample compilation tests

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 2:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Survey GAMSLIB corpus for syntax error indicators — tested 12+ models with `gams action=c`, estimated syntax error count, documented .lst error format
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Survey GAMSLIB corpus for syntax error indicators (Task 2)"
git push -u origin planning/sprint18-task2
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Survey GAMSLIB corpus for syntax error indicators (Task 2)" \
  --body "## Summary

Completed Task 2 of the Sprint 18 Preparation Plan: Survey GAMSLIB Corpus for Syntax Error Indicators.

### What was done
- Tested 12+ models with \`gams action=c\` (stratified sample)
- Documented GAMS exit code behavior and .lst error format
- Estimated syntax error count and impact on corpus denominator
- Cross-referenced pipeline failures with GAMS compilation results

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 1.1, 1.2, 1.3, 1.8)
- Updated \`PREP_PLAN.md\` (Task 2 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 2" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 3: Research GAMS `action=c` Compilation Mode

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task3
```

### Objective

Research GAMS `action=c` compilation mode thoroughly to inform the design of `scripts/gamslib/test_syntax.py`. Understand all relevant options, output formats, and edge cases.

### Why This Matters

The `test_syntax.py` script is a key Sprint 18 deliverable. If we misunderstand `action=c` behavior — exit codes, error output location, handling of `$include` files, or interaction with solver licensing — the script will need mid-sprint redesign.

### What Needs to Be Done

#### Step 1: GAMS Documentation Review (1 hour)

Research in GAMS documentation:
- Full specification of `action=c` behavior
- What errors are caught at compile time vs. execution time
- How `$include` files are resolved during compilation
- How compilation interacts with `$ontext`/`$offtext` blocks
- Whether `action=c` respects `$if`/`$else` conditionals
- Output file locations: .lst, .log, return code

#### Step 2: Hands-On Testing (1 hour)

Test various scenarios:

```bash
# Test 1: Clean model
gams himmel11.gms action=c
# Document: exit code, .lst content, .log content

# Test 2: Model with syntax error
gams camcge.gms action=c
# Document: exit code, error in .lst, error format

# Test 3: Model with $include
# Find a model using $include, test compilation
# Document: Does it follow includes? What if include file missing?

# Test 4: Model with runtime-only errors (e.g., division by zero in data)
# Document: Does action=c catch these or skip them?

# Test 5: Model with unresolved external references
# Document: Compilation error or runtime error?
```

#### Step 3: Design Script Interface (30 min)

Based on findings, document:
- Recommended command-line invocation for `test_syntax.py`
- How to capture and parse error output
- Timeout handling (some models may hang?)
- Batch execution strategy (sequential vs. parallel)
- Output format for `gams_syntax.status` field

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md` with findings
- Recommended `test_syntax.py` command-line interface
- Error parsing strategy documented

### Acceptance Criteria

- [ ] GAMS `action=c` behavior documented from official docs
- [ ] At least 5 test scenarios executed with results recorded
- [ ] Exit code semantics confirmed (0 = success, non-zero = error)
- [ ] .lst file error format documented for programmatic parsing
- [ ] Edge cases identified: `$include`, conditionals, timeouts
- [ ] `test_syntax.py` design sketch complete

### Verify Known Unknowns

This task verifies **Unknowns 1.1, 1.3, 1.7, 1.8** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 1.1** (Does `gams action=c` reliably detect all syntax errors?): Update with comprehensive test results, documenting reliability across different model types and error categories
- **Unknown 1.3** (Can GAMS .lst file error messages be parsed programmatically?): Update with detailed .lst format analysis, regex patterns identified, and any inconsistencies found
- **Unknown 1.7** (Does `gams action=c` require solver licensing?): Update with test results confirming whether compilation requires a solver license
- **Unknown 1.8** (What is the expected runtime for compiling all 160 models?): Update with per-model timing data and extrapolated total runtime

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 3:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Research GAMS `action=c` compilation mode — documented behavior, exit codes, .lst error format, edge cases, and `test_syntax.py` design sketch
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Research GAMS action=c compilation mode (Task 3)"
git push -u origin planning/sprint18-task3
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Research GAMS action=c compilation mode (Task 3)" \
  --body "## Summary

Completed Task 3 of the Sprint 18 Preparation Plan: Research GAMS \`action=c\` Compilation Mode.

### What was done
- Reviewed GAMS documentation for \`action=c\` specification
- Tested 5+ scenarios: clean model, syntax error, \$include, runtime errors, licensing
- Documented exit codes, .lst error format, and edge cases
- Designed \`test_syntax.py\` command-line interface

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 1.1, 1.3, 1.7, 1.8)
- Updated \`PREP_PLAN.md\` (Task 3 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 3" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 4: Analyze emit_gams.py Table Data Failures

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task4
```

### Objective

Analyze the `path_syntax_error` failures to identify which models fail specifically due to table data emission issues in `src/emit/original_symbols.py`, understand the root cause, and design the fix.

### Why This Matters

The Sprint 18 PROJECT_PLAN allocates 4-5 hours for table data emission fixes, targeting ~4 models. Before implementing, we need to confirm which models are affected, understand the exact failure mechanism, and design the fix. A wrong diagnosis would waste sprint time.

### What Needs to Be Done

#### Step 1: Identify Table Data Models (1 hour)

```bash
# Query database for path_syntax_error models
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f:
    db = json.load(f)
for name, entry in sorted(db.items()):
    status = entry.get('pipeline', {}).get('status', '')
    if status == 'path_syntax_error':
        print(f'{name}: {entry.get(\"pipeline\", {}).get(\"error_message\", \"\")[:100]}')
"
```

For each `path_syntax_error` model:
- Run the pipeline to reproduce the error
- Examine the generated MCP output
- Identify whether the error is in table data emission, parameter emission, or elsewhere
- Record: model name, error line, expected vs. actual output

#### Step 2: Examine Table Data Emission Code (1 hour)

Read `src/emit/original_symbols.py` and understand:
- How tables are currently emitted
- What table structures exist in GAMS (1-D, 2-D, multi-dimensional)
- Where the emission breaks down (missing data, wrong format, missing headers)
- What the correct GAMS table syntax should look like

#### Step 3: Design the Fix (1 hour)

For each identified failure:
- Document the root cause
- Propose a fix with code sketch
- Identify regression risk (will the fix break other models?)
- Estimate implementation time

#### Step 4: Create Test Cases (30 min)

For each affected model:
- Extract minimal table data that reproduces the issue
- Create unit test fixture
- Define expected output

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` with findings
- List of confirmed affected models
- Fix design with code sketches
- Unit test case definitions

### Acceptance Criteria

- [ ] All 17 `path_syntax_error` models cataloged by failure subcategory
- [ ] Models failing due to table data emission identified (exact list)
- [ ] Root cause traced to specific functions in `original_symbols.py`
- [ ] Fix designed with code sketch and regression risk assessment
- [ ] At least 2 unit test cases defined for the fix
- [ ] Estimated fix time validated (confirm 4-5h is realistic)

### Verify Known Unknowns

This task verifies **Unknowns 2.1, 2.3, 2.4, 2.6** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 2.1** (Which specific models fail due to table data emission?): Update with the exact list of affected models and the specific table structures causing failures
- **Unknown 2.3** (Are table data and computed parameters the top two emit_gams.py blockers?): Update with the full failure subcategory breakdown — confirm or correct the ranking
- **Unknown 2.4** (Does fixing table data emission require IR changes or only emitter changes?): Update with code-level analysis of whether `original_symbols.py` has sufficient information or if IR/parser changes are needed
- **Unknown 2.6** (What is the full `path_syntax_error` failure taxonomy?): Update with the complete categorization of all 17 `path_syntax_error` models

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 4:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Analyze emit_gams.py table data failures — cataloged all 17 `path_syntax_error` models, identified table data failures, designed fix with code sketch
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Analyze emit_gams.py table data failures (Task 4)"
git push -u origin planning/sprint18-task4
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Analyze emit_gams.py table data failures (Task 4)" \
  --body "## Summary

Completed Task 4 of the Sprint 18 Preparation Plan: Analyze emit_gams.py Table Data Failures.

### What was done
- Cataloged all 17 \`path_syntax_error\` models by failure subcategory
- Identified models failing due to table data emission
- Traced root causes to specific functions in \`original_symbols.py\`
- Designed fix with code sketch and regression risk assessment
- Defined unit test cases

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 2.1, 2.3, 2.4, 2.6)
- Updated \`PREP_PLAN.md\` (Task 4 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 4" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 5: Analyze emit_gams.py Computed Parameter Failures

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task5
```

### Objective

Analyze the `path_syntax_error` failures to identify which models fail specifically due to computed parameter assignment issues in `src/emit/original_symbols.py`, understand the root cause, and design the fix.

### Why This Matters

The Sprint 18 PROJECT_PLAN allocates 4-5 hours for computed parameter assignment fixes, targeting ~4 models. This is the second major emit_gams.py fix. Before implementing, we need to confirm which models are affected and understand the failure mechanism — computed parameters may involve expressions, conditional assignments, or loop-dependent values that require different handling than static parameter data.

### What Needs to Be Done

#### Step 1: Identify Computed Parameter Models (1 hour)

From the `path_syntax_error` models identified in Task 4:
- Isolate failures not related to table data
- Identify which are caused by computed parameter emission
- Record: model name, parameter involved, computation expression

#### Step 2: Examine Computed Parameter Emission Code (1 hour)

Read `src/emit/original_symbols.py` and understand:
- How parameter assignments are currently emitted
- How computed vs. static parameters are distinguished
- What happens with expression-based parameter values
- Where the emission fails (missing expression handling, wrong syntax)

#### Step 3: Design the Fix (1 hour)

For each identified failure:
- Document the root cause
- Propose a fix (re-emit expression vs. emit computed value)
- Assess whether the fix requires changes to the IR or just the emitter
- Identify regression risk

#### Step 4: Create Test Cases (30 min)

For each affected model:
- Extract minimal computed parameter that reproduces the issue
- Create unit test fixture
- Define expected output

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md` with findings
- List of confirmed affected models
- Fix design with approach decision documented
- Unit test case definitions

### Acceptance Criteria

- [ ] Models failing due to computed parameter emission identified (exact list)
- [ ] Root cause traced to specific functions in `original_symbols.py`
- [ ] Fix approach decided: re-emit expression vs. emit computed value
- [ ] Fix designed with code sketch and regression risk assessment
- [ ] At least 2 unit test cases defined for the fix
- [ ] Estimated fix time validated (confirm 4-5h is realistic)

### Verify Known Unknowns

This task verifies **Unknowns 2.2, 2.3, 2.5, 2.6** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 2.2** (Which specific models fail due to computed parameter assignments?): Update with the exact list of affected models, the parameters involved, and the types of computation expressions
- **Unknown 2.3** (Are table data and computed parameters the top two emit_gams.py blockers?): Update with confirmation or correction based on the full subcategory analysis from Tasks 4 and 5 combined
- **Unknown 2.5** (Should computed parameter fixes re-emit expressions or emit static values?): Update with the design decision and rationale — which approach is feasible given the IR representation?
- **Unknown 2.6** (What is the full `path_syntax_error` failure taxonomy?): Update with any additional subcategories discovered beyond what Task 4 found

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 5:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Analyze emit_gams.py computed parameter failures — identified affected models, decided fix approach (re-emit expression vs. emit static value), designed fix with code sketch
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Analyze emit_gams.py computed parameter failures (Task 5)"
git push -u origin planning/sprint18-task5
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Analyze emit_gams.py computed parameter failures (Task 5)" \
  --body "## Summary

Completed Task 5 of the Sprint 18 Preparation Plan: Analyze emit_gams.py Computed Parameter Failures.

### What was done
- Identified models failing due to computed parameter emission
- Traced root causes to specific functions in \`original_symbols.py\`
- Decided fix approach: re-emit expression vs. emit static values
- Designed fix with code sketch and regression risk assessment
- Defined unit test cases

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 2.2, 2.3, 2.5, 2.6)
- Updated \`PREP_PLAN.md\` (Task 5 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 5" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 6: Audit Put Statement `:width:decimals` Syntax

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task6
```

### Objective

Research the GAMS put statement `:width:decimals` format syntax, verify the affected models, and design the grammar extension for `src/gams/gams_grammar.lark`.

### Why This Matters

Sprint 18 includes a parse quick win: adding `:width:decimals` format specifiers to put statements. This is estimated at ~2 hours of sprint time and should unblock ~4 models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge). The prep task ensures the grammar change is well-understood before implementation.

### What Needs to Be Done

#### Step 1: GAMS Put Statement Specification (30 min)

Research the full put statement syntax from GAMS documentation:
- All format specifier variants (`:width`, `:width:decimals`, `:width:decimals:exponent`)
- Applicability to different put items (variables, parameters, text, expressions)
- Any interaction with put_page, put_utility, etc.

#### Step 2: Verify Affected Models (30 min)

For each of the 4 target models:
- Confirm the model fails due to `:width:decimals` syntax
- Check for any other blocking issues (secondary parse failures)
- Record the exact put statement line that fails

```bash
# Test each model
for model in ps5_s_mn ps10_s ps10_s_mn stdcge; do
    echo "=== $model ==="
    grep -n ':.*:' data/gamslib/models/$model.gms | head -5
done
```

#### Step 3: Design Grammar Extension (30 min)

Sketch the grammar change for `gams_grammar.lark`:
- Current put statement rule
- Required modifications to support `:width:decimals`
- Whether this affects the AST/IR or is handled at parse level only
- Potential conflicts with existing grammar rules

### Deliverables

- Put statement format syntax summary (in Known Unknowns or sprint notes)
- Confirmed list of affected models with specific failing lines
- Grammar extension design for `gams_grammar.lark`

### Acceptance Criteria

- [ ] GAMS put statement `:width:decimals` syntax fully documented
- [ ] All 4 target models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge) verified
- [ ] Any secondary blocking issues in target models identified
- [ ] Grammar extension designed for `gams_grammar.lark`
- [ ] Estimated fix time confirmed (~2 hours)

### Verify Known Unknowns

This task verifies **Unknowns 3.1, 3.2, 3.3, 3.4** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 3.1** (Is the `:width:decimals` syntax the only put statement format specifier?): Update with the full syntax specification from GAMS docs — document any additional variants like `:width:decimals:exponent`
- **Unknown 3.2** (Do the 4 target put-statement models have secondary blocking issues?): Update with per-model results — does each model parse successfully after removing the `:width:decimals` syntax?
- **Unknown 3.3** (Will the grammar extension conflict with existing colon usage in GAMS?): Update with analysis of existing colon usage in the grammar and any conflict risks
- **Unknown 3.4** (Are put statements semantically significant for MCP generation?): Update with confirmation that put statements are output-only and can be parsed and ignored for MCP purposes

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 6:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Audit put statement `:width:decimals` syntax — documented full format specifier syntax, verified 4 target models, designed grammar extension for `gams_grammar.lark`
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Audit put statement width:decimals syntax (Task 6)"
git push -u origin planning/sprint18-task6
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Audit put statement :width:decimals syntax (Task 6)" \
  --body "## Summary

Completed Task 6 of the Sprint 18 Preparation Plan: Audit Put Statement \`:width:decimals\` Syntax.

### What was done
- Researched full GAMS put statement format specifier syntax
- Verified all 4 target models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge)
- Checked for secondary blocking issues
- Designed grammar extension for \`gams_grammar.lark\`

### Deliverables
- Put statement syntax documentation
- Grammar extension design
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 3.1, 3.2, 3.3, 3.4)
- Updated \`PREP_PLAN.md\` (Task 6 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 6" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 7: Review Infeasible/Unbounded Model Status

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task7
```

### Objective

Investigate the 2 models currently flagged as `model_infeasible` and check for any unbounded models, to inform the corpus reclassification in Sprint 18.

### Why This Matters

Sprint 18 will reclassify syntax-error models as `excluded_syntax_error` and infeasible/unbounded models as `excluded_infeasible`/`excluded_unbounded`. Before building the reclassification, we need to understand the current state: Are these 2 models truly infeasible, or are they infeasible due to KKT formulation bugs? Should they be excluded from the corpus or investigated further?

### What Needs to Be Done

#### Step 1: Identify the 2 Infeasible Models (30 min)

```python
# Query database for model_infeasible
import json
with open('data/gamslib/gamslib_status.json') as f:
    db = json.load(f)
for name, entry in sorted(db.items()):
    status = entry.get('pipeline', {}).get('status', '')
    if status == 'model_infeasible':
        print(f'{name}: {json.dumps(entry, indent=2)}')
```

#### Step 2: Investigate Each Model (1-1.5 hours)

For each infeasible model:
- Read the original GAMS model source
- Solve the original NLP with GAMS to verify it has a feasible solution
- If NLP is feasible: the MCP formulation has a bug → keep in corpus, track as KKT issue
- If NLP is infeasible: confirm and document → candidate for exclusion

```bash
# Solve original NLP to check feasibility
gams <model>.gms
# Check: Model Status 1 = optimal (NLP is feasible)
# Check: Model Status 4 = infeasible (NLP truly infeasible)
```

#### Step 3: Check for Unbounded Models (30 min)

Review the database for any models showing unbounded indicators:
- GAMS solve status 3 (unbounded)
- PATH solve status indicating unboundedness
- Models with no finite bounds on objective-defining variables

#### Step 4: Document Findings (30 min)

For each infeasible/unbounded model:
- Is the infeasibility inherent or due to MCP formulation?
- Should it be excluded from corpus or kept as a bug to fix?
- What exclusion category applies?

### Deliverables

- Investigation report for each infeasible model (in Known Unknowns or separate doc)
- Determination: exclude or keep (with rationale)
- Unbounded model check results

### Acceptance Criteria

- [ ] Both `model_infeasible` models identified by name
- [ ] Original NLP solved with GAMS to confirm true feasibility status
- [ ] Each model classified: inherently infeasible vs. MCP formulation bug
- [ ] Exclusion/inclusion recommendation documented with rationale
- [ ] Unbounded model check completed across full corpus
- [ ] Findings integrated into Known Unknowns document

### Verify Known Unknowns

This task verifies **Unknowns 1.4, 1.5** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 1.4** (Are the 2 `model_infeasible` models inherently infeasible or MCP formulation bugs?): Update with the names of both models, the NLP solve results, and the determination (inherent infeasibility vs. KKT bug) with evidence
- **Unknown 1.5** (What exclusion categories should the database support?): Update with findings about what types of exclusions are actually needed based on the infeasible/unbounded investigation — confirm or expand the three-category assumption

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 7:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Review infeasible/unbounded model status — investigated 2 `model_infeasible` models, determined exclusion vs. retention, checked for unbounded models
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Review infeasible/unbounded model status (Task 7)"
git push -u origin planning/sprint18-task7
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Review infeasible/unbounded model status (Task 7)" \
  --body "## Summary

Completed Task 7 of the Sprint 18 Preparation Plan: Review Infeasible/Unbounded Model Status.

### What was done
- Identified and investigated both \`model_infeasible\` models
- Solved original NLPs with GAMS to confirm true feasibility status
- Classified each model: inherently infeasible vs. MCP formulation bug
- Checked full corpus for unbounded models
- Documented exclusion/inclusion recommendations with rationale

### Deliverables
- Investigation report for each infeasible model
- Exclusion/inclusion recommendations
- Unbounded model check results
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 1.4, 1.5)
- Updated \`PREP_PLAN.md\` (Task 7 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 7" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 8: Design Corpus Reclassification Schema

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task8
```

### Objective

Design the database schema changes and reclassification logic for `gamslib_status.json` to support the new syntactic validation categories. This ensures Sprint 18 implementation proceeds smoothly without mid-sprint schema debates.

### Why This Matters

Sprint 18 will add a `gams_syntax.status` field to the database and reclassify models as `excluded_syntax_error`, `excluded_infeasible`, or `excluded_unbounded`. The schema design affects how metrics are calculated, how reporting handles excluded models, and whether existing scripts need updates. Getting the schema right during prep prevents rework during the sprint.

### What Needs to Be Done

#### Step 1: Review Current Schema (30 min)

Read `data/gamslib/gamslib_status.json` and `src/reporting/` to understand:
- Current database structure and conventions
- How metrics are calculated from the database
- Which scripts query the database and what fields they expect

#### Step 2: Design Schema Changes (1 hour)

Design the new fields:
- Where does `gams_syntax` live in the document hierarchy?
- How does exclusion status interact with `pipeline.status`?
- Should excluded models retain their pipeline status or be overwritten?
- How should metrics scripts handle the reduced corpus?

Proposed schema:
```json
{
    "model_name": {
        "metadata": { "type": "NLP", "convex": true },
        "gams_syntax": {
            "status": "valid|syntax_error|compilation_error",
            "error_message": "...",
            "error_line": 42,
            "tested_date": "2026-02-XX"
        },
        "exclusion": {
            "excluded": false,
            "reason": null,
            "category": null
        },
        "pipeline": { "status": "path_syntax_error" }
    }
}
```

#### Step 3: Design Metrics Recalculation (30 min)

Document how metrics should change:
- Valid corpus = total models - excluded models
- Parse rate = parsed / valid corpus (not total)
- All downstream metrics use valid corpus as denominator
- Track both "total corpus" and "valid corpus" metrics for transparency

#### Step 4: Identify Reporting Script Changes (30 min)

Review `src/reporting/` and identify which files need updates:
- `status_analyzer.py` — needs to filter excluded models
- `failure_analyzer.py` — needs to handle new failure categories
- `progress_analyzer.py` — needs valid corpus denominator
- `generate_report.py` — needs to report exclusions

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md` with complete schema design
- JSON schema examples for each exclusion category
- Metrics recalculation rules
- List of affected reporting scripts with required changes

### Acceptance Criteria

- [ ] New `gams_syntax` fields defined with types and semantics
- [ ] Exclusion mechanism designed (flag vs. status vs. separate field)
- [ ] Metrics recalculation rules documented (valid corpus denominator)
- [ ] All affected reporting scripts identified with change descriptions
- [ ] Schema handles edge cases (excluded model with existing pipeline data)
- [ ] Design reviewed for backward compatibility with existing tooling

### Verify Known Unknowns

This task verifies **Unknowns 1.5, 1.6, 4.2** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 1.5** (What exclusion categories should the database support?): Update with the final schema design — confirm three categories are sufficient or document additional categories needed
- **Unknown 1.6** (How should metrics be recalculated with a reduced valid corpus?): Update with the metrics recalculation rules, how to present the change, and which reporting scripts need modifications
- **Unknown 4.2** (Does the database schema support adding new fields without breaking existing tools?): Update with the results of reviewing reporting scripts — confirm they use flexible field access or document what needs to change

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 8:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Design corpus reclassification schema — defined `gams_syntax` and `exclusion` fields, documented metrics recalculation rules, identified reporting script changes
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Design corpus reclassification schema (Task 8)"
git push -u origin planning/sprint18-task8
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Design corpus reclassification schema (Task 8)" \
  --body "## Summary

Completed Task 8 of the Sprint 18 Preparation Plan: Design Corpus Reclassification Schema.

### What was done
- Reviewed current \`gamslib_status.json\` schema and reporting scripts
- Designed \`gams_syntax\` and \`exclusion\` fields with types and semantics
- Documented metrics recalculation rules (valid corpus denominator)
- Identified all affected reporting scripts with required change descriptions
- Verified backward compatibility with existing tooling

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 1.5, 1.6, 4.2)
- Updated \`PREP_PLAN.md\` (Task 8 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 8" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 9: Verify Sprint 18 Baseline Metrics

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task9
```

### Objective

Verify that the v1.1.0 baseline metrics (Parse 61/160, Translate 42/61, Solve 12/42, Full Pipeline 12/160) are accurate and reproducible on the current main branch.

### Why This Matters

Sprint 18 acceptance criteria are defined relative to the v1.1.0 baseline. If the baseline is incorrect — due to flaky tests, environment differences, or database staleness — then Sprint 18 progress measurement will be unreliable. The Sprint 17 retrospective already identified confusion between solve success and full pipeline metrics; we must start Sprint 18 with clean, verified numbers.

### What Needs to Be Done

#### Step 1: Run Full Test Suite (30 min)

```bash
# Verify all tests pass on main
git checkout main
pytest tests/ -v --tb=short
# Expected: 3204 tests, all passing
```

#### Step 2: Run Pipeline on Full Corpus (30 min)

```bash
# Re-run pipeline metrics
python scripts/gamslib/run_full_test.py
# Verify parse/translate/solve counts match v1.1.0 numbers
```

#### Step 3: Verify Database State (30 min)

```python
# Count pipeline statuses
import json
from collections import Counter

with open('data/gamslib/gamslib_status.json') as f:
    db = json.load(f)

statuses = Counter()
for name, entry in db.items():
    status = entry.get('pipeline', {}).get('status', 'unknown')
    statuses[status] += 1

for status, count in statuses.most_common():
    print(f'{status}: {count}')
```

Verify counts match:
- 61 models with successful parse
- 42 models with successful translate
- 12 models with `model_optimal` solve status
- Remaining 99 models with various error statuses summing to 99

#### Step 4: Document Verified Baseline (15 min)

Create a verified baseline record that Sprint 18 can reference:
- Exact counts for each pipeline stage
- Exact error category breakdown
- Git commit hash of baseline
- Date of verification

### Deliverables

- Verified baseline record (counts, commit hash, date)
- Discrepancy report (if any numbers don't match)
- Confirmation that Sprint 18 acceptance criteria baselines are accurate

### Acceptance Criteria

- [ ] Full test suite passes on main (3204+ tests)
- [ ] Parse count verified: 61/160
- [ ] Translate count verified: 42/61
- [ ] Solve count verified: 12/42
- [ ] Error category breakdown matches Sprint 17 retrospective
- [ ] Any discrepancies documented and resolved
- [ ] Baseline commit hash recorded

### Verify Known Unknowns

This task verifies **Unknowns 4.1, 4.3, 4.4** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 4.1** (Is the v1.1.0 baseline accurate and reproducible?): Update with the verified counts, any discrepancies found, and the confirmed baseline commit hash
- **Unknown 4.3** (Should Sprint 18 re-run the solution comparison stage?): Update with the comparison infrastructure status — is it functional? How long does it take? Should it be included in the Sprint 18 pipeline retest?
- **Unknown 4.4** (Are there any GAMS environment changes since v1.1.0 that could affect results?): Update with the current GAMS version, PATH solver version, and any environment changes detected

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 9:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Verify Sprint 18 baseline metrics — confirmed v1.1.0 baseline (Parse 61/160, Translate 42/61, Solve 12/42), all 3204+ tests passing, baseline commit hash recorded
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Verify Sprint 18 baseline metrics (Task 9)"
git push -u origin planning/sprint18-task9
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Verify Sprint 18 baseline metrics (Task 9)" \
  --body "## Summary

Completed Task 9 of the Sprint 18 Preparation Plan: Verify Sprint 18 Baseline Metrics.

### What was done
- Ran full test suite on main (3204+ tests)
- Re-ran pipeline on full corpus to verify parse/translate/solve counts
- Verified database state matches v1.1.0 reported metrics
- Documented verified baseline with commit hash and date
- Checked GAMS environment for any changes since Sprint 17

### Deliverables
- Verified baseline record
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 4.1, 4.3, 4.4)
- Updated \`PREP_PLAN.md\` (Task 9 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 9" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.

---

## Task 10: Plan Sprint 18 Detailed Schedule

### Branch

```
git checkout main && git pull
git checkout -b planning/sprint18-task10
```

### Objective

Create a detailed day-by-day schedule for Sprint 18, incorporating all findings from the prep tasks. This ensures smooth execution with clear daily goals, checkpoints, and contingency plans.

### Why This Matters

Sprint 18 has 22-26 hours of estimated work across 3 components. A detailed schedule ensures work is sequenced to maximize early feedback, emit_gams.py fixes are informed by prep analysis, and checkpoints catch problems early.

### What Needs to Be Done

#### Step 1: Incorporate Prep Findings (1 hour)

Review all prep task deliverables:
- Task 1: Known Unknowns — any unresolved Critical unknowns?
- Task 2: Corpus Survey — how many syntax errors expected?
- Task 3: GAMS action=c Research — any surprises affecting script design?
- Task 4: Table Data Analysis — confirmed models and fix design
- Task 5: Computed Param Analysis — confirmed models and fix approach
- Task 6: Put Statement Audit — confirmed models and grammar design
- Task 7: Infeasible/Unbounded Review — exclusion recommendations
- Task 8: Schema Design — ready for implementation?
- Task 9: Baseline Verification — confirmed numbers?

#### Step 2: Create Day-by-Day Plan (1.5 hours)

Tentative schedule (adjust based on prep findings):

| Day | Focus | Deliverables | Hours |
|-----|-------|-------------|-------|
| 1 | test_syntax.py implementation | Script running on all 160 models | 3h |
| 2 | SYNTAX_ERROR_REPORT.md + corpus reclassification | Report generated, schema updated | 3h |
| 3 | Infeasible/unbounded docs + checkpoint | Exclusions documented, metrics recalculated | 2h |
| 4 | emit_gams.py: table data emission | Fix implemented with tests | 3h |
| 5 | emit_gams.py: computed parameter assignments | Fix implemented with tests | 3h |
| 6 | Pipeline retest + checkpoint | Updated metrics, progress report | 2h |
| 7 | Parse quick win: put statement format | Grammar extended, 4 models unblocked | 2h |
| 8 | Integration testing + buffer | Full regression, fix any issues | 2-3h |
| 9 | Documentation + checkpoint | Sprint 18 retrospective draft | 2h |
| 10 | Release prep + final metrics | Sprint 18 complete | 2h |

#### Step 3: Define Checkpoints (30 min)

Using checkpoint templates from Epic 1:
- **Checkpoint 1 (Day 3):** Syntactic validation complete, corpus redefined
- **Checkpoint 2 (Day 6):** emit_gams.py fixes complete, pipeline retested
- **Checkpoint 3 (Day 9):** All components complete, documentation ready

#### Step 4: Define Contingency Plans (30 min)

For each risk:
- Syntactic validation finds many more errors than expected → adjust scope
- emit_gams.py fixes harder than analyzed → deprioritize parse quick win
- Put statement models have secondary blockers → document and defer
- Baseline metrics don't match → investigate before proceeding

#### Step 5: Write Sprint 18 Plan Document (30 min)

Compile into `docs/planning/EPIC_4/SPRINT_18/PLAN.md`:
- Sprint goals (from PROJECT_PLAN.md)
- Day-by-day schedule
- Checkpoint definitions
- Contingency plans
- Success criteria
- References to prep deliverables

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/PLAN.md` with complete sprint plan
- Day-by-day schedule with deliverables
- Checkpoint definitions
- Contingency plans

### Acceptance Criteria

- [ ] Day-by-day schedule covers all 3 Sprint 18 components
- [ ] Schedule incorporates findings from all 9 prep tasks
- [ ] 3 checkpoints defined with clear go/no-go criteria
- [ ] Contingency plans documented for top risks
- [ ] Total estimated hours match PROJECT_PLAN.md (22-26h)
- [ ] References to all prep deliverables included
- [ ] Plan reviewed for feasibility within 10 working days

### Verify Known Unknowns

This task verifies **Unknowns 2.7, 2.8** from `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`.

For each unknown, update the `KNOWN_UNKNOWNS.md` Verification Results section:
- **Unknown 2.7** (Will emit_gams.py fixes break currently-solving models?): Update with the regression testing plan — how the schedule ensures the 12 currently-solving models are retested after each fix, and what happens if a regression is detected
- **Unknown 2.8** (How will the pipeline retest be structured after emit_gams.py fixes?): Update with the Day 6 retest plan — scope (all models vs. valid corpus), stages included (comparison or not), and success criteria

For each, change the status from `🔍 **Status:** INCOMPLETE` to either:
- `✅ **Status:** VERIFIED` — assumption confirmed with evidence
- `❌ **Status:** WRONG` — assumption incorrect, document the correction

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md`, update Task 10:
1. Change `**Status:** Not Started` to `**Status:** ✅ **COMPLETED** (date)`
2. Fill in the **Changes** section with actual files created/modified
3. Fill in the **Result** section with actual findings
4. Check off all acceptance criteria that were met: `- [ ]` → `- [x]`

### Update CHANGELOG.md

Add an entry under the `[Unreleased]` section:

```markdown
### Research
- Plan Sprint 18 detailed schedule — created day-by-day plan with checkpoints, contingency plans, and prep findings integrated
```

### Quality Gate

Before committing, run:

```bash
make typecheck && make lint && make format && make test
```

All must pass. If any fail, fix the issues before proceeding.

### Commit

```bash
git add -A
git commit -m "prep: Plan Sprint 18 detailed schedule (Task 10)"
git push -u origin planning/sprint18-task10
```

### Create Pull Request

```bash
gh pr create \
  --title "prep: Plan Sprint 18 detailed schedule (Task 10)" \
  --body "## Summary

Completed Task 10 of the Sprint 18 Preparation Plan: Plan Sprint 18 Detailed Schedule.

### What was done
- Reviewed all 9 prep task deliverables for findings and risks
- Created day-by-day schedule across 10 working days (22-26h)
- Defined 3 checkpoints with go/no-go criteria (Days 3, 6, 9)
- Documented contingency plans for top risks
- Integrated all prep findings into schedule

### Deliverables
- \`docs/planning/EPIC_4/SPRINT_18/PLAN.md\`
- Updated \`KNOWN_UNKNOWNS.md\` (Unknowns 2.7, 2.8)
- Updated \`PREP_PLAN.md\` (Task 10 status)
- Updated \`CHANGELOG.md\`

### Quality
- \`make typecheck\` ✅
- \`make lint\` ✅
- \`make format\` ✅
- \`make test\` ✅

**Ref:** Sprint 18 Prep Plan Task 10" \
  --base main
```

Then **wait for reviewer comments** before merging. If review comments are received, address them following the same quality gate process.
