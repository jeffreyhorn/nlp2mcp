# Sprint 18 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 18 production work begins
**Timeline:** Complete before Sprint 18 Day 1
**Goal:** Prepare for GAMSLIB Syntactic Validation, emit_gams.py Solve Fixes & Parse Quick Wins

**Key Context from Epic 3 Final (v1.1.0):** Baseline metrics — Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%), Full Pipeline 12/160 (7.5%). Sprint 18 is the first sprint of Epic 4, targeting full GAMSLIB LP/NLP/QCP coverage.

---

## Executive Summary

Sprint 18 marks the beginning of Epic 4, which aims to achieve full pipeline success for all syntactically correct, feasible GAMSLIB convex models. The sprint has three major components:

1. **GAMSLIB Syntactic Correctness Validation (~10-12h):** Create `test_syntax.py`, generate a syntax error report, reclassify the corpus, and document infeasible/unbounded models.
2. **emit_gams.py Solve Fixes — Part 1 (~10-12h):** Fix table data emission and computed parameter assignments in `src/emit/original_symbols.py` to unblock ~8 models.
3. **Parse Quick Win: Put Statement Format (~2h):** Add `:width:decimals` syntax support to unblock ~4 models.

This prep plan focuses on research, analysis, and setup tasks that must be completed before Sprint 18 Day 1 to prevent blocking issues and ensure smooth execution.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 18 Component Addressed |
|---|------|----------|-----------|--------------|-------------------------------|
| 1 | Create Sprint 18 Known Unknowns List | Critical | 3-4 hours | None | All components — proactive unknown identification |
| 2 | Survey GAMSLIB Corpus for Syntax Error Indicators | High | 2-3 hours | None | Syntactic Validation — understand scope before building |
| 3 | Research GAMS `action=c` Compilation Mode | High | 2-3 hours | None | Syntactic Validation — script design |
| 4 | Analyze emit_gams.py Table Data Failures | Critical | 3-4 hours | None | emit_gams.py Solve Fixes — understand blockers |
| 5 | Analyze emit_gams.py Computed Parameter Failures | Critical | 3-4 hours | None | emit_gams.py Solve Fixes — understand blockers |
| 6 | Audit Put Statement `:width:decimals` Syntax | Medium | 1-2 hours | None | Parse Quick Win — grammar design |
| 7 | Review Infeasible/Unbounded Model Status | High | 2-3 hours | Task 2 | Syntactic Validation — corpus reclassification |
| 8 | Design Corpus Reclassification Schema | High | 2-3 hours | Tasks 2, 7 | Syntactic Validation — database changes |
| 9 | Verify Sprint 18 Baseline Metrics | High | 1-2 hours | None | All — ensure v1.1.0 baseline is accurate |
| 10 | Plan Sprint 18 Detailed Schedule | Critical | 3-4 hours | All tasks | Sprint 18 planning |

**Total Estimated Time (roll-up):** 27 hours (P50), with a working range of 24-30 hours (~3 working days + up to ~1 extra day buffer)

**Variance Allocation / Critical Path:** The majority of the uncertainty is on the critical path — Tasks 1 → 4/5 → 10:
- Task 1: ±1 hour depending on discovery scope
- Tasks 4 & 5: ±1 hour each depending on complexity of emit_gams.py failures
- Task 10: ±1 hour to incorporate findings from earlier analysis tasks

This makes the schedule risk explicit while keeping the base plan at ~27 hours and a bounded variance of ±3 hours focused on critical-path work.

---

## Task 1: Create Sprint 18 Known Unknowns List

**Status:** ✅ **COMPLETED** (February 5, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** First prep task — complete before all others
**Owner:** Development team
**Dependencies:** None

### Objective

Create a comprehensive list of assumptions and unknowns for Sprint 18 to prevent late-discovery issues. This continues the Known Unknowns practice that achieved high ratings in earlier sprints.

### Why This Matters

Sprint 18 introduces a new capability (GAMS compilation testing) and tackles emit_gams.py bugs that were deprioritized in Sprint 17. Both areas have unresolved assumptions that could derail the sprint if discovered late. The Known Unknowns process proactively surfaces these risks.

### Background

Epic 4 Sprint 18 has three components per `docs/planning/EPIC_4/PROJECT_PLAN.md`:
- GAMSLIB Syntactic Correctness Validation (new capability, ~10-12h)
- emit_gams.py Solve Fixes Part 1 (deferred from Sprint 17, ~10-12h)
- Parse Quick Win: Put Statement Format (~2h)

Each component carries assumptions about GAMS behavior, model characteristics, and code structure that need verification.

### What Needs to Be Done

#### Category 1: GAMSLIB Syntactic Validation Unknowns

| Unknown | Assumption | How to Verify | Priority |
|---------|-----------|---------------|----------|
| Does `gams action=c` work on all 160 models? | Yes, standard GAMS feature | Test on 5 sample models | Critical |
| What exit code does GAMS return on syntax error? | Non-zero exit code | Test with known bad model (camcge) | Critical |
| Are there models that compile but have runtime errors? | Not relevant for syntax check | `action=c` only compiles, doesn't execute | High |
| How many models actually have GAMS syntax errors? | Estimate 5-15 | Run survey (Task 2) | High |
| Do our `lexer_invalid_char` failures correlate with GAMS syntax errors? | Some overlap expected | Cross-reference after running test_syntax.py | Medium |
| Can GAMS compilation error messages be parsed programmatically? | Yes, consistent format in .lst file | Examine .lst output format | High |

#### Category 2: emit_gams.py Unknowns

| Unknown | Assumption | How to Verify | Priority |
|---------|-----------|---------------|----------|
| Which specific models fail due to table data emission? | ~4 models | Analyze path_syntax_error failures | Critical |
| Which models fail due to computed parameter assignments? | ~4 models | Analyze path_syntax_error failures | Critical |
| Are table data and computed parameters the top two emit_gams.py blockers? | Yes, per Sprint 17 analysis | Re-verify with current codebase | High |
| Does `original_symbols.py` have the right hooks for table data? | Needs investigation | Read source code | High |
| Are there other emit_gams.py issues beyond table data and computed params? | Possibly, need to check remaining path_syntax_error models | Analyze all 17 path_syntax_error failures | High |
| Will fixing table data/computed params actually unblock 8 models? | Estimated, not confirmed | Verify model-by-model after analysis | Medium |

#### Category 3: Parse Quick Win Unknowns

| Unknown | Assumption | How to Verify | Priority |
|---------|-----------|---------------|----------|
| Is the `:width:decimals` syntax documented in GAMS reference? | Yes | Check GAMS documentation | Medium |
| Are there other put statement syntax variants we're missing? | Possibly | Review GAMS put statement spec | Medium |
| Do the 4 target models have other blocking issues? | May have secondary issues | Run pipeline on each after fix | Low |

#### Category 4: Infrastructure & Process Unknowns

| Unknown | Assumption | How to Verify | Priority |
|---------|-----------|---------------|----------|
| Is the v1.1.0 baseline accurate and reproducible? | Yes, was tagged | Re-run pipeline metrics | High |
| Are all 3204 tests still passing on main? | Yes | Run full test suite | High |
| Does the database schema support the new `gams_syntax.status` field? | Needs to be added | Review gamslib_status.json structure | Medium |
| Should excluded models use a new status or a flag? | Design decision | Task 8 | Medium |

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`

**Contents:**
- 20+ unknowns across 4 categories
- Each unknown has: assumption, verification method, priority, risk-if-wrong
- Verification deadlines assigned (prep phase vs Day 1-2)
- Template for tracking resolution during sprint

### Result

A comprehensive Known Unknowns document that:
- Surfaces all assumptions before Sprint 18 begins
- Assigns verification methods and deadlines to each unknown
- Provides a living document for tracking during the sprint
- Prevents late-discovery issues that could derail the sprint

### Verification

- Document created at `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md`
- Minimum 20 unknowns identified across all 4 categories
- All Critical/High unknowns have a concrete verification plan
- Verification deadlines assigned (most resolved during prep, remainder by Day 2)

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` with 20+ unknowns
- Each unknown categorized, prioritized, and assigned a verification method
- Template for adding newly discovered unknowns during the sprint

### Acceptance Criteria

- [x] Document created with 20+ unknowns across 4 categories
- [x] All unknowns have assumption, verification method, and priority
- [x] All Critical/High unknowns have verification plan with deadline
- [x] Unknowns cover all 3 Sprint 18 components plus infrastructure
- [x] Template for updates during sprint defined
- [x] Research time for verification estimated

---

## Task 2: Survey GAMSLIB Corpus for Syntax Error Indicators

**Status:** ✅ **COMPLETED** (February 5, 2026)
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Task 8 (corpus reclassification design)
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.8

### Objective

Survey the 160 convex GAMSLIB models to estimate how many have GAMS-level syntax errors, understand what types of errors exist, and scope the syntactic validation work for Sprint 18.

### Why This Matters

Sprint 18's syntactic validation component assumes some models in the corpus have GAMS-level syntax errors. Before building `test_syntax.py`, we need to understand the scope: Are there 2 models or 20? What kinds of errors exist? This survey informs time estimates and the syntax error report format.

### Background

From Sprint 17 retrospective and Epic 4 GOALS.md:
- `camcge` is known to have mismatched parentheses (a GAMS syntax error)
- 74 models fail with `lexer_invalid_char` — some may be nlp2mcp grammar gaps, others may be GAMS syntax issues
- 2 models flagged as `model_infeasible` need separate investigation
- The current `gamslib_status.json` database tracks pipeline status but not GAMS compilation status

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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md`

**Contents:**
- Full corpus compilation test results (160 models tested, 160/160 OK)
- Cross-reference of pipeline failures vs. GAMS compilation failures
- Finding: Zero GAMS syntax errors in corpus
- Impact analysis: No corpus reduction needed, Sprint 18 scope simplified

### Result

**KEY FINDING: Zero GAMS syntax errors in the 160-model corpus.**

- All 160 models compile successfully with `gams action=c`
- All 99 nlp2mcp parse failures are due to nlp2mcp grammar limitations, NOT GAMS issues
- `camcge` compiles successfully — the `lexer_invalid_char` error is due to multi-line continuation nlp2mcp doesn't handle
- The `syntax_error` exclusion reason currently has count 0 (no models require it), but remains supported in the schema for future discoveries
- Sprint 18 syntactic validation component is ~50% simpler than originally planned
- Corpus denominator remains 160 (no reduction)

### Verification

- All 160 models tested with `gams action=c` (exceeded 12+ requirement)
- Exit code 0 for success, 2 for errors documented
- .lst error format documented with regex patterns
- Zero syntax errors found (not 5-15 as assumed)
- Complete cross-reference with pipeline failures

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` with survey results
- Full test results (160/160 models compile OK)
- Updated scope estimate for Sprint 18 syntactic validation component
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 1.3, 1.8

### Acceptance Criteria

- [x] At least 12 models tested with `gams action=c` (stratified sample) — **EXCEEDED: All 160 tested**
- [x] GAMS exit code behavior documented for success and failure
- [x] .lst file error format documented (for programmatic parsing)
- [x] Estimated number of syntax-error models (range) — **FINDING: Zero errors**
- [x] Cross-reference with nlp2mcp pipeline failures complete
- [x] Impact on corpus denominator estimated — **No reduction needed**

---

## Task 3: Research GAMS `action=c` Compilation Mode

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 1.1, 1.3, 1.7, 1.8

### Objective

Research GAMS `action=c` compilation mode thoroughly to inform the design of `scripts/gamslib/test_syntax.py`. Understand all relevant options, output formats, and edge cases.

### Why This Matters

The `test_syntax.py` script is a key Sprint 18 deliverable. If we misunderstand `action=c` behavior — exit codes, error output location, handling of `$include` files, or interaction with solver licensing — the script will need mid-sprint redesign.

### Background

GAMS supports several "action" modes that control how far processing proceeds:
- `action=c` — Compile only (syntax check, no execution)
- `action=ce` — Compile and execute (no solve)
- `action=r` — Restart from a save file

For syntactic validation, `action=c` is the right choice: it checks syntax without requiring solver licenses or data files.

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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md`

**Contents:**
- GAMS `action=c` specification summary from official documentation
- Test results for 10 scenarios (exceeded 5 requirement)
- Error output format documentation with regex patterns
- Complete `test_syntax.py` design with command-line interface, batch strategy, and status values

### Result

Complete research documenting GAMS `action=c` behavior:

**Key Findings:**
1. Exit codes: 0 = success, 2 = compilation error (reliable and consistent)
2. .lst error format is parseable with provided regex patterns
3. `$include` files are followed during compilation
4. `$if/$else` conditionals are processed correctly
5. `solve` statements compile but don't invoke solvers (no license needed)
6. Runtime errors (div/0) NOT detected (correct — only syntax checked)
7. Performance: ~0.16s per model, 160 models in ~26s
8. Solver licensing NOT required for `action=c` mode

**test_syntax.py Design:**
- Command: `gams <model.gms> action=c lo=0 o=<tempfile.lst>`
- Timeout: 30 seconds (generous buffer)
- Status values: `valid`, `syntax_error`, `timeout`, `error`
- Batch strategy: Sequential (fast enough, no parallelization needed)
- Error parsing: Regex patterns provided for `.lst` file parsing

### Verification

- GAMS documentation reviewed and key behaviors noted
- 10 test scenarios executed and documented (exceeded 5 requirement)
- Error output format confirmed with regex patterns for programmatic parsing
- All edge cases covered: `$include`, conditionals, solve statements, solver licensing, timeouts

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md` with complete findings
- Recommended `test_syntax.py` command-line interface and design
- Error parsing strategy with regex patterns
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.3, 1.7, 1.8

### Acceptance Criteria

- [x] GAMS `action=c` behavior documented from official docs
- [x] At least 5 test scenarios executed with results recorded — **EXCEEDED: 10 scenarios**
- [x] Exit code semantics confirmed (0 = success, 2 = error)
- [x] .lst file error format documented for programmatic parsing
- [x] Edge cases identified: `$include`, conditionals, timeouts, solver licensing
- [x] `test_syntax.py` design sketch complete

---

## Task 4: Analyze emit_gams.py Table Data Failures

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 2.1, 2.3, 2.4, 2.6

### Objective

Analyze the `path_syntax_error` failures to identify which models fail specifically due to table data emission issues in `src/emit/original_symbols.py`, understand the root cause, and design the fix.

### Why This Matters

The Sprint 18 PROJECT_PLAN allocates 4-5 hours for table data emission fixes, targeting ~4 models. Before implementing, we need to confirm which models are affected, understand the exact failure mechanism, and design the fix. A wrong diagnosis would waste sprint time.

### Background

From the Sprint 17 retrospective, 17 models fail with `path_syntax_error`. These are models that parse and translate successfully but produce GAMS MCP output that fails to compile. The Sprint 17 deferred items identified table data emission and computed parameter assignments as the top two emit_gams.py blockers.

Key files:
- `src/emit/original_symbols.py` — Emits original GAMS symbols (sets, parameters, tables, variables) into MCP output
- `src/emit/model.py` — Emits model structure (equations, solve statement)
- `data/gamslib/gamslib_status.json` — Pipeline status database

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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md`

**Contents:**
- Complete taxonomy of all 17 `path_syntax_error` models by failure category
- Detailed GAMS compilation error analysis with error codes
- 6 distinct failure categories identified (not 2 as originally assumed)
- Root cause analysis traced to specific code locations
- Fix designs with code sketches for top 3 priorities
- 3 unit test case definitions

### Result

**KEY FINDING: Table data emission is NOT a blocker.**

Complete analysis revealed a different failure taxonomy than originally assumed:
- **0 models** fail due to table data emission (tables work correctly)
- **5 models** fail due to computed parameter assignment emission
- **5 models** fail due to bound multiplier variable dimension issues
- **6 models** fail due to set element quoting (ps2_* family + pollut)
- **3 models** fail due to multi-dimensional parameter data
- **1 model** fails due to undefined function reference (psi)
- **1 model** fails due to MCP mapping issues

**Sprint 18 scope adjustment recommended:** Drop table data fix (0h saved), prioritize set element quoting (2-3h, 6 models) and skip computed params (2h, 5 models).

### Verification

- All 17 `path_syntax_error` models compiled with `gams action=c`
- GAMS error codes extracted and categorized
- Root causes traced to specific emit modules
- Fix designs include code sketches and regression risk

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` with complete findings
- Full taxonomy of 17 models by 6 failure categories
- Fix designs with code sketches for priorities 1-3
- 3 unit test case definitions
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.3, 2.4, 2.6

### Acceptance Criteria

- [x] All 17 `path_syntax_error` models cataloged by failure subcategory
- [x] Models failing due to table data emission identified (exact list) — **FINDING: 0 models**
- [x] Root cause traced to specific functions in `original_symbols.py` and other emit modules
- [x] Fix designed with code sketch and regression risk assessment
- [x] At least 2 unit test cases defined for the fix — **3 test cases defined**
- [x] Estimated fix time validated — **Table fix: 0h (not needed); Computed param skip: 2h; Set quoting: 2-3h**

---

## Task 5: Analyze emit_gams.py Computed Parameter Failures

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 2.2, 2.3, 2.5, 2.6

### Objective

Analyze the `path_syntax_error` failures to identify which models fail specifically due to computed parameter assignment issues in `src/emit/original_symbols.py`, understand the root cause, and design the fix.

### Why This Matters

The Sprint 18 PROJECT_PLAN allocates 4-5 hours for computed parameter assignment fixes, targeting ~4 models. This is the second major emit_gams.py fix. Before implementing, we need to confirm which models are affected and understand the failure mechanism — computed parameters may involve expressions, conditional assignments, or loop-dependent values that require different handling than static parameter data.

### Background

Computed parameters in GAMS differ from static parameter data:
- Static: `Parameter a / 1 2.5, 2 3.7 /;`
- Computed: `a(i) = sum(j, b(i,j) * c(j));`

The emit_gams.py code needs to reproduce computed parameter values in the MCP output. If the computation depends on other model data, the emission must either:
1. Re-emit the computation expression, or
2. Emit the computed values as static data

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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md`

**Contents:**
- Complete analysis of 5 affected models (ajax, demo1, mathopt1, mexss, sample)
- Root cause analysis: post-solve reporting (2 models), pre-processing with dependencies (3 models)
- Code-level diagnosis in `emit_computed_parameter_assignments()`
- Fix design: SKIP all computed parameter assignments (Option A)
- 3 unit test case definitions

### Result

**KEY FINDING: Computed parameter assignments should be SKIPPED entirely.**

Analysis of all 5 affected models reveals:
- **All 5 models** use computed parameters for purposes NOT needed in MCP (reporting, pre-processing)
- **The assignments fail** due to ordering issues, missing dependencies, or set element quoting
- **The MCP model works correctly** without these assignments
- **Recommended fix:** Skip `emit_computed_parameter_assignments()` entirely

| Model | Parameters | Purpose | Needed for MCP? |
|-------|-----------|---------|-----------------|
| ajax | `mtr`, `par` | Intermediate calc | No |
| demo1 | `croprep`, `labrep` | Post-solve reporting | No |
| mathopt1 | `report` | Post-solve comparison | No |
| mexss | `d`, `muf`, `muv`, `mue`, `pd`, `pv`, `pe` | Pre-processing | No |
| sample | `w`, `tpop`, `k1`, `k2` | Pre-processing | No |

**Sprint 18 fix:** 2 hours (skip function) instead of 8-10 hours (complex re-emit)

### Verification

- All 5 computed parameter models identified with exact parameter lists
- Root cause traced to `emit_computed_parameter_assignments()` in `original_symbols.py`
- Fix approach decided: SKIP (not re-emit or static values)
- 3 unit test cases defined
- Verified 12 currently-solving models don't use computed param assignments

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md` with complete findings
- List of 5 confirmed affected models with parameter details
- Fix design: SKIP approach with code sketch
- 3 unit test case definitions
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.2, 2.3, 2.5, 2.6

### Acceptance Criteria

- [x] Models failing due to computed parameter emission identified (exact list)
- [x] Root cause traced to specific functions in `original_symbols.py`
- [x] Fix approach decided: re-emit expression vs. emit computed value — **Decision: SKIP**
- [x] Fix designed with code sketch and regression risk assessment
- [x] At least 2 unit test cases defined for the fix — **3 test cases defined**
- [x] Estimated fix time validated — **2h (not 4-5h) due to simple skip approach**

---

## Task 6: Audit Put Statement `:width:decimals` Syntax

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** Medium
**Estimated Time:** 1-2 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Research the GAMS put statement `:width:decimals` format syntax, verify the affected models, and design the grammar extension for `src/gams/gams_grammar.lark`.

### Why This Matters

Sprint 18 includes a parse quick win: adding `:width:decimals` format specifiers to put statements. This is estimated at ~2 hours of sprint time. The prep task ensures the grammar change is well-understood before implementation.

**Note:** Analysis revealed that 3 models (ps5_s_mn, ps10_s, ps10_s_mn) are blocked by `:width:decimals` syntax, while stdcge requires a separate `put_stmt_nosemi` fix. See Key Findings below for details.

### Background

GAMS put statements support format specifiers for controlling output width and decimal places:
```gams
put x:10:4;     * width 10, 4 decimal places
put x:0:6;      * minimum width, 6 decimal places
put 'text':20;  * text with width 20
```

The current grammar in `src/gams/gams_grammar.lark` handles basic put statements but not the `:width:decimals` suffix.

### What Needs to Be Done

#### Step 1: GAMS Put Statement Specification (30 min)

Research the full put statement syntax from GAMS documentation:
- All format specifier variants (`:width`, `:width:decimals`) — **verified: no `:width:decimals:exponent` variant exists**
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

### Changes

- **Created:** `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` — complete analysis document
- **Updated:** `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` — Unknowns 3.1, 3.2, 3.3, 3.4 verified

### Result

**Key Findings:**

| Finding | Details |
|---------|---------|
| Format syntax | Supports `:width` and `:width:decimals`; no `:width:decimals:exponent` variant |
| Alignment option | Optional `<`, `>`, `<>` prefix: `item:<10:5` |
| Models affected | **3 models** (not 4) — ps5_s_mn, ps10_s, ps10_s_mn |
| stdcge issue | Different blocker: needs `put_stmt_nosemi` for loop context |
| Grammar conflict | None — colon is context-specific to put_item |
| Semantic significance | None — put statements are output-only, safe to ignore for MCP |

**Grammar Extension Design:**
```lark
put_item: STRING put_format?
        | "/" -> put_newline
        | expr put_format?

put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?
PUT_ALIGN: "<>" | "<" | ">"
```

**Additional Fix Needed:** `put_stmt_nosemi` variant for stdcge (~30 min extra)

### Verification

- [x] GAMS put statement format syntax documented
- [x] All 4 target models verified — 3 blocked by `:width:decimals`, 1 (stdcge) blocked by different issue
- [x] Grammar extension sketched in Lark syntax
- [x] Secondary blocking issues documented (stdcge needs `put_stmt_nosemi`)

### Deliverables

- [x] Put statement format syntax summary in `PUT_FORMAT_ANALYSIS.md`
- [x] Confirmed list of affected models with specific failing lines
- [x] Grammar extension design for `gams_grammar.lark`
- [x] Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [x] GAMS put statement `:width:decimals` syntax fully documented
- [x] All 4 target models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge) verified
- [x] Any secondary blocking issues in target models identified
- [x] Grammar extension designed for `gams_grammar.lark`
- [x] Estimated fix time confirmed (~2 hours for both fixes)

---

## Task 7: Review Infeasible/Unbounded Model Status

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Task 8 (corpus reclassification design)
**Owner:** Development team
**Dependencies:** Task 2 (corpus survey provides context)
**Unknowns Verified:** 1.4, 1.5

### Objective

Investigate the 2 models currently flagged as `model_infeasible` and check for any unbounded models, to inform the corpus reclassification in Sprint 18.

### Why This Matters

Sprint 18 will reclassify syntax-error models with `exclusion.reason = "syntax_error"`. Excluding models based on infeasible/unbounded status would require a future schema change and is out of scope for Sprint 18. Before building the reclassification, we need to understand the current state: Are these 2 models truly infeasible, or are they infeasible due to KKT formulation bugs? Should they be excluded from the corpus or investigated further (outside the Sprint 18 schema work)?

### Background

From the Sprint 17 remaining blockers:
- 2 models flagged as `model_infeasible` — these might be:
  - Inherently infeasible NLP models (no feasible solution exists)
  - Models where the MCP formulation is incorrect (KKT bug)
  - Models where PATH can't find a solution (convergence issue, not true infeasibility)

Additionally, some models might be unbounded (no finite optimum), which would produce degenerate KKT conditions.

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
# Check model status: 1 = optimal, 4 = infeasible, 5 = locally infeasible
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

### Changes

- **Updated:** `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` — Unknowns 1.4, 1.5 verified

### Result

**Key Findings:**

| Model | MCP Status | Original NLP Status | Determination |
|-------|------------|---------------------|---------------|
| circle | Locally Infeasible | **Optimal** (obj=5.277) | KKT bug - keep in corpus |
| house | Locally Infeasible | **Optimal** (obj=4500) | KKT bug - keep in corpus |

**Root causes:**
- **circle:** Uses `uniform()` for random data — MCP regenerates different points than NLP
- **house:** Likely constraint qualification failure or incorrect Lagrangian formulation

**Unbounded models:** None found in corpus

**Exclusion categories needed (updated plan):**
- `exclusion.reason = "syntax_error"` — Yes (for future syntax error discoveries)
- Add `infeasible` to enum? — No (both infeasible models are MCP bugs, not inherently infeasible; this overturns the earlier Task 7 assumption that Sprint 18 would introduce an infeasible exclusion bucket)
- Add `unbounded` to enum? — No (no unbounded models found; this likewise supersedes the earlier plan to add an unbounded exclusion bucket)

### Verification

- [x] Both `model_infeasible` models investigated (circle, house)
- [x] Original NLP solve status checked for each (both optimal)
- [x] Determination (inherent vs. bug) documented with evidence
- [x] Unbounded model check completed (none found)

### Deliverables

- Investigation report for each infeasible model (in Known Unknowns or separate doc)
- Determination: exclude or keep (with rationale)
- Unbounded model check results
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.4, 1.5

### Acceptance Criteria

- [x] Both `model_infeasible` models identified by name (circle, house)
- [x] Original NLP solved with GAMS to confirm true feasibility status (both optimal)
- [x] Each model classified: inherently infeasible vs. MCP formulation bug (both MCP bugs)
- [x] Exclusion/inclusion recommendation documented with rationale (keep both in corpus)
- [x] Unbounded model check completed across full corpus (none found)
- [x] Findings integrated into Known Unknowns document (Unknowns 1.4, 1.5 verified)

---

## Task 8: Design Corpus Reclassification Schema

**Status:** Complete
**Priority:** High
**Estimated Time:** 2-3 hours
**Actual Time:** 2 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** Task 2 (survey scope), Task 7 (infeasible/unbounded investigation)
**Unknowns Verified:** 1.5, 1.6, 4.2

### Objective

Design the database schema changes and reclassification logic for `gamslib_status.json` to support the new syntactic validation categories. This ensures Sprint 18 implementation proceeds smoothly without mid-sprint schema debates.

### Why This Matters (updated plan)

Sprint 18 will add a `gams_syntax` field to track GAMS compilation validation results. Based on Task 7 findings:
- Only `syntax_error` as `exclusion.reason` is needed (not `infeasible` or `unbounded`)
- Both `model_infeasible` models (circle, house) are MCP formulation bugs, not candidates for exclusion

The schema design affects:
- How metrics are calculated (valid corpus denominator)
- How the reporting infrastructure handles excluded models
- Whether existing scripts (generate_report.py, failure analysis) need updates

Getting the schema right during prep prevents rework during the sprint.

### Background

Current `gamslib_status.json` structure (models array with entries):
```json
{
  "models": [
    {
      "model_id": "example",
      "model_name": "Example Model",
      "gamslib_type": "NLP",
      "nlp2mcp_parse": { "status": "success", ... },
      "mcp_solve": { "status": "failure", "outcome_category": "path_syntax_error", ... },
      "solution_comparison": { ... }
    }
  ]
}
```

Sprint 18 needs to add (see SCHEMA_DESIGN.md for complete specification):
- `gams_syntax.status`: "success", "failure", "not_tested"
- `gams_syntax.errors[]`: Array of error details (code, message, line)
- `exclusion.excluded`: Boolean flag for corpus exclusion
- `exclusion.reason`: "syntax_error" (via `exclusion.reason` field)

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

Proposed schema (see SCHEMA_DESIGN.md for complete specification):
```json
{
  "models": [
    {
      "model_id": "example",
      "gams_syntax": {
        "status": "success|failure|not_tested",
        "errors": [{ "code": 148, "message": "...", "line": 42 }]
      },
      "exclusion": {
        "excluded": false
      },
      "nlp2mcp_parse": { "status": "success", ... }
    }
  ]
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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md`

**Contents:**
- Current schema summary
- Proposed schema changes with JSON examples
- Metrics recalculation rules
- Reporting script change inventory

### Result

A complete schema design that Sprint 18 can implement directly:
- New fields defined with types and semantics
- Metrics recalculation rules documented
- Reporting script changes identified
- No mid-sprint debates about data model

### Verification

- Schema design reviewed for consistency with existing conventions
- Metrics recalculation rules are unambiguous
- All affected scripts identified
- Design handles edge cases (model excluded after partial pipeline success)

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md` with complete schema design
- JSON schema examples for each exclusion category
- Metrics recalculation rules
- List of affected reporting scripts with required changes
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.5, 1.6, 4.2

### Acceptance Criteria

- [x] New `gams_syntax` fields defined with types and semantics
- [x] Exclusion mechanism designed (flag vs. status vs. separate field)
- [x] Metrics recalculation rules documented (valid corpus denominator)
- [x] All affected reporting scripts identified with change descriptions
- [x] Schema handles edge cases (excluded model with existing pipeline data)
- [x] Design reviewed for backward compatibility with existing tooling

### Results

**Task 8 completed February 6, 2026.**

**Key deliverables:**
- `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md` created with:
  - `gams_syntax` field definition (status, validation_date, gams_version, errors array)
  - `exclusion` field definition (excluded boolean, reason enum, details)
  - Metrics recalculation rules (valid_corpus = total - excluded)
  - Reporting script impact analysis (no immediate changes needed since 0 exclusions)
  - Migration strategy and implementation checklist

**Key findings:**
1. Only `syntax_error` exclusion reason needed (not infeasible/unbounded per Task 7)
2. Schema bump: `2.0.0` → `2.1.0` (minor, backward-compatible)
3. No reporting script changes needed until exclusions are added
4. `baseline_metrics.json` separate from `gamslib_status.json` — simplifies transition

**Unknowns verified:**
- Unknown 1.5: Only `syntax_error` exclusion reason needed ✅
- Unknown 1.6: Metrics recalculation rules documented ✅
- Unknown 4.2: Schema extensibility confirmed safe ✅

---

## Task 9: Verify Sprint 18 Baseline Metrics

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** High
**Estimated Time:** 1-2 hours
**Actual Time:** 1.5 hours
**Deadline:** Before Sprint 18 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 4.1, 4.3, 4.4

### Objective

Verify that the v1.1.0 baseline metrics (Parse 61/160, Translate 42/61, Solve 12/42, Full Pipeline 12/160) are accurate and reproducible on the current main branch.

### Why This Matters

Sprint 18 acceptance criteria are defined relative to the v1.1.0 baseline. If the baseline is incorrect — due to flaky tests, environment differences, or database staleness — then Sprint 18 progress measurement will be unreliable. The Sprint 17 retrospective already identified confusion between solve success and full pipeline metrics; we must start Sprint 18 with clean, verified numbers.

### Background

From the Sprint 17 retrospective and SUMMARY.md:
- Parse: 61/160 (38.1%)
- Translate: 42/61 (68.9%)
- Solve: 12/42 (28.6%) — solve-stage success (PATH `model_optimal`)
- Full Pipeline: 12/160 (7.5%) — note: Sprint 17 did not re-run comparison stage
- Tests: 3204

Key concern: The "Full Pipeline" metric of 12/160 uses solve-stage success as a proxy because solution comparison was not re-run in Sprint 17. The true full pipeline (with comparison match) was 5/160 in Sprint 16.

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
python scripts/gamslib/run_pipeline.py
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

### Changes

**No files created** — baseline verified and recorded in Sprint 18 planning notes.

### Result

Confirmed, reproducible baseline metrics for Sprint 18:
- All numbers verified against actual database state
- Any discrepancies identified and resolved
- Clear reference point for measuring Sprint 18 progress

### Verification

- Full test suite passes (3204 tests)
- Pipeline metrics match v1.1.0 numbers
- Database state consistent with reported metrics
- Error category counts sum correctly

### Deliverables

- Verified baseline record (counts, commit hash, date)
- Discrepancy report (if any numbers don't match)
- Confirmation that Sprint 18 acceptance criteria baselines are accurate
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.3, 4.4

### Acceptance Criteria

- [x] Full test suite passes on main (3204+ tests, with expected skips/xfail)
- [x] Parse count verified: 61/160
- [x] Translate count verified: 42/61
- [x] Solve count verified: 12/42
- [x] Error category breakdown matches Sprint 17 retrospective (see error categories below)
- [x] Any discrepancies documented and resolved
- [x] Baseline commit hash recorded

### Results

**Task 9 completed February 6, 2026.**

**Verified baseline metrics:**

| Metric | Expected | Verified | Status |
|--------|----------|----------|--------|
| Test suite | 3204+ pass | 3204 passed, 10 skipped, 1 xfailed | ✅ |
| Parse success | 61 | 61 | ✅ |
| Parse failure | 99 | 99 | ✅ |
| Translate success | 42 | 42 | ✅ |
| Translate failure | 19 | 19 | ✅ |
| Solve (model_optimal) | 12 | 12 | ✅ |
| Convex models (corpus) | 160 | 160 | ✅ |

**Error category breakdown (verified against gamslib_status.json):**
- Parse errors: `lexer_invalid_char` (74), `internal_error` (23), `semantic_undefined_symbol` (2)
- Translate errors: `unsup_index_offset` (8), `internal_error` (5), `codegen_numerical_error` (2), `unsup_expression_type` (2), `diff_unsupported_func` (2)
- Solve outcomes: `model_optimal` (12), `path_syntax_error` (17), `path_solve_terminated` (11), `model_infeasible` (2)

**Verified 12 model_optimal models:** apl1p, blend, himmel11, hs62, mathopt2, mhw4d, mhw4dx, prodmix, rbrock, trig, trnsport, trussm

**GAMS environment verified:**
- GAMS Version: 51.3.0 (38407a9b, Oct 27, 2025)
- PATH Solver: 103001 (libpath52.dylib)
- Platform: macOS (DEX-DEG x86 64bit)

**Baseline verification:**
- Commit hash: `aed804ae50d2296464b17dfe22b6c8e69edf236d`
- Verification date: February 6, 2026
- Verification PR: #643

**Unknowns verified:**
- Unknown 4.1: v1.1.0 baseline is accurate and reproducible ✅
- Unknown 4.3: Solution comparison not needed for baseline verification ✅
- Unknown 4.4: GAMS environment unchanged since v1.1.0 ✅

---

## Task 10: Plan Sprint 18 Detailed Schedule

**Status:** ✅ **COMPLETED** (February 6, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Actual Time:** 2.5 hours
**Deadline:** Final prep task — complete after all others
**Owner:** Development team
**Dependencies:** All preceding tasks (1-9)
**Unknowns Verified:** 2.7, 2.8

### Objective

Create a detailed day-by-day schedule for Sprint 18, incorporating all findings from the prep tasks. This ensures smooth execution with clear daily goals, checkpoints, and contingency plans.

### Why This Matters

Sprint 18 has 22-26 hours of estimated work across 3 components. A detailed schedule ensures:
- Work is sequenced to maximize early feedback
- Syntactic validation (new capability) gets priority
- emit_gams.py fixes are informed by prep analysis
- Parse quick win is slotted efficiently
- Checkpoints catch problems early

### Background

From `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 18:
- **Component 1:** GAMSLIB Syntactic Correctness Validation (~10-12h)
  - test_syntax.py script (4-5h)
  - SYNTAX_ERROR_REPORT.md (2-3h)
  - Corpus reclassification (2h)
  - Infeasible/unbounded documentation (2h)
- **Component 2:** emit_gams.py Solve Fixes Part 1 (~10-12h)
  - Table data emission (4-5h)
  - Computed parameter assignments (4-5h)
  - Pipeline retest (2h)
- **Component 3:** Parse Quick Win: Put Statement Format (~2h)

Total: 22-26 hours across 10 working days

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

### Changes

**File Created:** `docs/planning/EPIC_4/SPRINT_18/PLAN.md`

**Contents:**
- Sprint 18 goals and success criteria
- Day-by-day schedule with hour estimates
- Checkpoint definitions (Days 3, 6, 9)
- Contingency plans for identified risks
- References to all prep task deliverables

### Result

A complete Sprint 18 plan that:
- Sequences work for maximum early feedback
- Incorporates all prep findings
- Has clear checkpoints and contingency plans
- Is ready for execution on Day 1

### Verification

- Schedule totals 22-26 hours across 10 days
- All 3 Sprint 18 components have scheduled days
- Checkpoints are scheduled and have clear criteria
- Contingency plans cover all identified risks
- Prep task findings are integrated

### Deliverables

- `docs/planning/EPIC_4/SPRINT_18/PLAN.md` with complete sprint plan
- Day-by-day schedule with deliverables
- Checkpoint definitions
- Contingency plans
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.7, 2.8

### Acceptance Criteria

- [x] Day-by-day schedule covers all 3 Sprint 18 components
- [x] Schedule incorporates findings from all 9 prep tasks
- [x] 3 checkpoints defined with clear go/no-go criteria
- [x] Contingency plans documented for top risks
- [x] Total estimated hours revised to 16-20h based on removed items; PROJECT_PLAN.md (currently 22-26h) identified for update in Sprint 18
- [x] References to all prep deliverables included
- [x] Plan reviewed for feasibility within 10 working days

### Results

**Task 10 completed February 6, 2026.**

**Key scope changes identified:**

| Category | Removed Items | Added Items |
|----------|---------------|-------------|
| Syntactic Validation | Syntax Error Report (2-3h), Infeasible/Unbounded Docs (2h) | — |
| emit_gams.py | Table Data Emission (4-5h) | Set Element Quoting (2-3h), Bound Multiplier Dimension (4-5h) |
| Parse Quick Win | — | stdcge `put_stmt_nosemi` (+0.5h) |

**Removed items (not needed based on prep findings):**
1. Table data emission fix — zero models fail due to table data (Task 4)
2. Syntax Error Report with details — zero GAMS syntax errors found (Task 2)
3. Infeasible/unbounded documentation — both are MCP bugs, not exclusions (Task 7)

**Added items (new priorities from prep findings):**
1. Set element quoting fix — 6 models blocked (Task 4), highest ROI
2. Bound multiplier dimension fix — 5 models blocked (Task 4)
3. stdcge `put_stmt_nosemi` — different issue than `:width:decimals` (Task 6)

**Time savings:** 6 hours freed up for buffer/contingency

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_18/PLAN.md` — complete sprint plan with revised scope
- Updated `KNOWN_UNKNOWNS.md` — Unknowns 2.7, 2.8 verified

**Unknowns verified:**
- Unknown 2.7: Regression testing plan defined (after-each-fix + Day 6 full retest) ✅
- Unknown 2.8: Day 6 retest scope and success criteria defined ✅

---

## Summary

### Total Estimated Time: 27 hours (P50), working range 24-30 hours (~3 working days + up to ~1 extra day buffer)

### Critical Path

```
Task 1 (Known Unknowns) ──→ Task 10 (Sprint Plan)
         │
         ├── Task 4 (Table Data) ──→ Task 10
         ├── Task 5 (Computed Params) ──→ Task 10
         │
Task 2 (Corpus Survey) ──→ Task 7 (Infeasible) ──→ Task 8 (Schema) ──→ Task 10
         │
Task 3 (action=c Research) ──→ Task 10
Task 6 (Put Statement) ──→ Task 10
Task 9 (Baseline Verification) ──→ Task 10
```

### Success Criteria

All 10 prep tasks completed before Sprint 18 Day 1:
1. Known Unknowns document created with 20+ unknowns
2. Corpus survey complete with syntax error estimates
3. GAMS `action=c` behavior fully understood
4. Table data emission failures analyzed with fix design
5. Computed parameter emission failures analyzed with fix design
6. Put statement format syntax researched with grammar design
7. Infeasible/unbounded models investigated with recommendations
8. Corpus reclassification schema designed
9. Baseline metrics verified and confirmed
10. Sprint 18 detailed schedule created

### Document Cross-References

| Document | Purpose | Location |
|----------|---------|----------|
| Epic 4 Goals | Strategic goals for Sprints 18-25 | `docs/planning/EPIC_4/GOALS.md` |
| Epic 4 Project Plan | Sprint-by-sprint breakdown | `docs/planning/EPIC_4/PROJECT_PLAN.md` |
| Sprint 17 Retrospective | Lessons learned, deferred work | `docs/planning/EPIC_3/SPRINT_17/SPRINT_RETROSPECTIVE.md` |
| Epic 3 Summary | Cumulative metrics and progress | `docs/planning/EPIC_3/SUMMARY.md` |
| GAMSLIB Status Database | Pipeline status for all models | `data/gamslib/gamslib_status.json` |
| Reporting Module | Metrics and analysis scripts | `src/reporting/` |
| Emit Module | GAMS code generation (fix target) | `src/emit/original_symbols.py` |
| Grammar File | Lark grammar (parse quick win target) | `src/gams/gams_grammar.lark` |

---

## Appendix: Sprint 18 Acceptance Criteria (from PROJECT_PLAN.md)

For reference, Sprint 18 must meet these criteria upon completion:

- **Syntactic Validation:** All 160 models tested for GAMS compilation
- **Corpus Defined:** Valid corpus established with excluded models documented
- **emit_gams.py:** Table data and computed parameter fixes merged with tests
- **Put Statement:** Format syntax supported, 4 target models unblocked
- **Metrics:** `path_syntax_error` count reduced by ≥6 from baseline (17)
- **Quality:** All existing 3204+ tests still pass; new fixes have regression tests
