# Sprint 21 Preparation Task Prompts

**Purpose:** Self-contained prompts for executing each Sprint 21 prep task (Tasks 2–10).
**Usage:** Copy a prompt into a new Claude Code session to execute the task autonomously.
**Prerequisites:** Task 1 (Known Unknowns) is complete. Branch `planning/sprint21-prep` exists.

**Standing instructions:**
- Never put "Co-authored-by" in commit messages or comments
- PR review replies: ALWAYS use `gh api "repos/jeffreyhorn/nlp2mcp/pulls/NNN/comments/$COMMENT_ID/replies" -X POST -f body="..."` to reply directly to individual comments

---

## Task 2: Research GAMS Macro Expansion Semantics

````
On a new branch `planning/sprint21-task2` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 2: Research GAMS Macro Expansion Semantics.

### OBJECTIVE

Research GAMS `$set`/`$eval` directive semantics and `%name%` macro expansion to produce a design document for the preprocessor macro subsystem (Sprint 21 Priority 1).

Sprint 21 Priority 1 (4–8h) depends entirely on understanding the GAMS macro expansion model. The preprocessor currently strips `$set`/`$eval` directives without executing them. Two models are immediately blocked: saras (`%system.nlp%`) and springchain (`$set`/`$eval`/`%N%`/`%NM1%`).

### WHAT NEEDS TO BE DONE

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

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/MACRO_EXPANSION_DESIGN.md` — design document with architecture, scope, and test plan
- Corpus survey results: count and classification of macro usage patterns across 160 models
- Updated `KNOWN_UNKNOWNS.md` Category 1 unknowns marked as resolved
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 1.3, 1.4

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 1.1:** Is simple string substitution sufficient for `$eval` expressions in GAMSlib?
- Assumption: `$eval` uses only simple integer arithmetic
- Verify by examining springchain.gms `$eval` lines and surveying corpus

**Unknown 1.2:** How many GAMSlib models use compile-time macros beyond saras and springchain?
- Assumption: Only saras and springchain are blocked by macro expansion
- Verify by grepping for `$set`, `$setglobal`, `$eval`, `%name%` across corpus

**Unknown 1.3:** What system macros (`%system.X%`) does GAMS support, and which are needed?
- Assumption: `%system.nlp%` returns solver name; no other system macros used in corpus
- Verify by reading saras.gms and searching GAMS docs

**Unknown 1.4:** Should macro expansion happen before or after other preprocessing steps?
- Assumption: Macro expansion should be first preprocessing step
- Verify by checking GAMS processing order and testing edge cases

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 2 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Macro expansion design document completed" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the Task 1 entry, before Sprint 20 Day 14):

```
### Sprint 21 Prep Task 2: Research GAMS Macro Expansion Semantics - YYYY-MM-DD

**Branch:** `planning/sprint21-task2`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 2: Research GAMS Macro Expansion Semantics

- Created MACRO_EXPANSION_DESIGN.md with preprocessor architecture
- Surveyed GAMSlib corpus for macro usage patterns
- Verified Known Unknowns 1.1, 1.2, 1.3, 1.4
- Updated PREP_PLAN.md Task 2 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 2: Research GAMS Macro Expansion Semantics" --body "$(cat <<'EOF'
## Summary
- Researched GAMS `$set`/`$eval`/`%name%` macro expansion semantics
- Created `MACRO_EXPANSION_DESIGN.md` with preprocessor architecture, scope, and test plan
- Surveyed GAMSlib corpus for macro usage patterns
- Verified Known Unknowns 1.1, 1.2, 1.3, 1.4 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] Design document covers all identified macro patterns
- [ ] Corpus survey results are reproducible
- [ ] All 4 Category 1 unknowns have verification results
- [ ] PREP_PLAN.md Task 2 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 3: Catalog internal_error Root Causes (7 Models)

````
On a new branch `planning/sprint21-task3` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 3: Catalog internal_error Root Causes (7 Models).

### OBJECTIVE

Run the 7 internal_error models through `parse_file()`, capture the error tracebacks, and classify root causes into subcategories to enable prioritized fixes during Sprint 21 Priority 2.

Sprint 21 Priority 2 allocates 6–10h to fix 7 internal_error models. A root cause catalog enables batch fixes and accurate effort estimates, mirroring the Sprint 20 lexer error subcategory catalog methodology.

### WHAT NEEDS TO BE DONE

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
   - A: Table row index mismatch
   - B: Lead/lag syntax not handled in IR builder
   - C: Undefined symbol reference during IR construction
   - D: Other (document each individually)
4. **Count models per subcategory** and identify batch-fix opportunities
5. **Estimate fix effort** per subcategory (1h, 2h, 4h)
6. **Write catalog document** with per-model findings and recommended fix order

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md` — per-model root cause analysis with subcategory classification
- Recommended fix order based on batch-fix potential and model count
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.2, 2.3

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 2.1:** Do the 7 internal_error models fail for the same IR builder reason or distinct reasons?
- Assumption: 2–3 distinct root causes, enabling batch fixes
- Verify by running all 7 models and comparing tracebacks

**Unknown 2.2:** Are any internal_error models blocked by lead/lag syntax (`x(t-1)`, `x(t+1)`)?
- Assumption: Lead/lag is NOT the primary blocker
- Verify by grepping for lead/lag patterns and checking tracebacks

**Unknown 2.3:** Can internal_error models be fixed incrementally, or do they require architectural changes?
- Assumption: Each model can be fixed with targeted, incremental changes
- Verify by assessing each fix as A (handler/case), B (grammar+handler), or C (architecture)

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 3 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "internal_error root cause catalog completed (7 models)" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 3: Catalog internal_error Root Causes - YYYY-MM-DD

**Branch:** `planning/sprint21-task3`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 3: Catalog internal_error Root Causes

- Created INTERNAL_ERROR_CATALOG.md with 7-model root cause analysis
- Classified root causes into subcategories with batch-fix opportunities
- Verified Known Unknowns 2.1, 2.2, 2.3
- Updated PREP_PLAN.md Task 3 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 3: Catalog internal_error Root Causes (7 Models)" --body "$(cat <<'EOF'
## Summary
- Ran 7 internal_error models through `parse_file()` with full traceback capture
- Classified root causes into subcategories with batch-fix opportunities
- Created `INTERNAL_ERROR_CATALOG.md` with per-model analysis and recommended fix order
- Verified Known Unknowns 2.1, 2.2, 2.3 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] All 7 models have traceback analysis
- [ ] Root causes classified into subcategories
- [ ] Fix effort estimated per subcategory
- [ ] All 3 Category 2 unknowns have verification results
- [ ] PREP_PLAN.md Task 3 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 4: Catalog path_syntax_error Root Causes (45 Models)

````
On a new branch `planning/sprint21-task4` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 4: Catalog path_syntax_error Root Causes (45 Models).

### OBJECTIVE

Run the 45 path_syntax_error models through the full pipeline, capture the PATH error output, and classify root causes into subcategories. This is the largest single error population and the key to Sprint 21 Priority 3 (8–12h budget).

### WHAT NEEDS TO BE DONE

1. **Get the list of 45 path_syntax_error models** from `data/gamslib/gamslib_status.json`
   - Note: models are a list of objects, not a dict. Each has `model_id`, `mcp_solve.status`, etc.
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

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — subcategory classification with model counts and root cause analysis
- Prioritized fix order based on model count per subcategory and estimated effort
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 3.1:** Are the 45 path_syntax_error models caused by a few root causes or many distinct issues?
- Assumption: 4–6 root cause subcategories, top 2–3 accounting for 30+ models
- Verify by clustering PATH error messages from representative sample

**Unknown 3.2:** Is the MCP Model statement generated correctly for all equation-variable pairings?
- Assumption: Emitter correctly generates Model statement pairings
- Verify by comparing working vs. failing model Model statements

**Unknown 3.3:** Are there GAMS identifier naming rules that the emitter violates?
- Assumption: All generated identifiers are GAMS-legal (≤63 chars, no reserved keywords)
- Verify by checking identifier lengths and names in generated MCP files

**Unknown 3.4:** How many path_syntax_error models fail due to translate-stage issues vs. emitter-stage issues?
- Assumption: Most fail due to emitter-stage issues (formatting, Model statement)
- Verify by attempting to compile MCP files and separating compile vs. solve errors

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 4 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "path_syntax_error root cause catalog completed (45 models)" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 4: Catalog path_syntax_error Root Causes - YYYY-MM-DD

**Branch:** `planning/sprint21-task4`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 4: Catalog path_syntax_error Root Causes

- Created PATH_SYNTAX_ERROR_CATALOG.md with 45-model root cause analysis
- Classified into subcategories with model counts and fix effort estimates
- Verified Known Unknowns 3.1, 3.2, 3.3, 3.4
- Updated PREP_PLAN.md Task 4 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 4: Catalog path_syntax_error Root Causes (45 Models)" --body "$(cat <<'EOF'
## Summary
- Analyzed 45 path_syntax_error models and classified into root cause subcategories
- Created `PATH_SYNTAX_ERROR_CATALOG.md` with model counts and recommended attack order
- Identified highest-leverage fixes for Sprint 21 Priority 3
- Verified Known Unknowns 3.1, 3.2, 3.3, 3.4 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] At least 15–20 models analyzed in detail
- [ ] Root causes classified into subcategories with counts
- [ ] Fix effort estimated per subcategory
- [ ] All 4 Category 3 unknowns have verification results
- [ ] PREP_PLAN.md Task 4 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 5: Triage Deferred Sprint 20 Issues

````
On a new branch `planning/sprint21-task5` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 5: Triage Deferred Sprint 20 Issues.

IMPORTANT: This task depends on Tasks 3 and 4. If Tasks 3 and 4 have NOT been merged into `planning/sprint21-prep` yet, branch from whichever task branch is most current, or wait for them to merge.

### OBJECTIVE

Review all 13 deferred Sprint 20 issues, assess current status, identify overlaps with other Sprint 21 priorities, and recommend which to tackle in Sprint 21 vs. defer further.

Sprint 21 Priority 4 allocates 8–12h for 13 deferred issues. Triaging now prevents wasting sprint time on issues that should be deferred and identifies overlap with Priorities 1–3.

### WHAT NEEDS TO BE DONE

1. **Review each of the 10 active issue files** in `docs/issues/` (not all 13 have files; some may be in `docs/issues/completed/`):

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

2. **For each issue, assess:**
   - Current status: still blocked? partially resolved? resolved by Sprint 20 work?
   - Overlap with Sprint 21 priorities (e.g., #837/#840 → Priority 1 macro expansion)
   - Estimated fix effort (in Sprint 21 context, with new capabilities)
   - Dependencies on other Sprint 21 work
3. **Categorize each issue:**
   - **Do in Sprint 21:** tractable, high leverage, overlaps with planned work
   - **Defer to Sprint 22+:** requires architectural change, low leverage, blocked by external factors
4. **Create prioritized triage document** with recommendations

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` — per-issue assessment with Sprint 21 / defer recommendation
- Overlap map showing which deferred issues are addressed by Sprint 21 Priority 1–3 work
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.3

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 4.1:** Which of the 13 deferred issues overlap with Sprint 21 Priority 1–3 work?
- Assumption: #837 and #840 fully overlap with Priority 1 (macro expansion)
- Verify by cross-referencing issue model names with internal_error and path_syntax_error lists

**Unknown 4.2:** Is the gastrans Jacobian timeout (#830) a fundamental performance issue or a dynamic subset bug?
- Assumption: Dynamic subset expansion causes exponential Jacobian blowup
- Verify by profiling or analyzing the Jacobian computation structure

**Unknown 4.3:** Can the min/max objective reformulation issue (#789) be resolved within Sprint 21's scope?
- Assumption: Targeted fix to KKT assembly or emitter, no fundamental redesign
- Verify by reading the issue file and tracing spurious variable generation

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 5 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Deferred issues triaged (13 issues, do/defer categorization)" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 5: Triage Deferred Sprint 20 Issues - YYYY-MM-DD

**Branch:** `planning/sprint21-task5`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 5: Triage Deferred Sprint 20 Issues

- Created DEFERRED_ISSUES_TRIAGE.md with 13-issue assessment
- Categorized each as "Do in Sprint 21" or "Defer to Sprint 22+"
- Identified overlaps with Sprint 21 Priorities 1-3
- Verified Known Unknowns 4.1, 4.2, 4.3
- Updated PREP_PLAN.md Task 5 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 5: Triage Deferred Sprint 20 Issues" --body "$(cat <<'EOF'
## Summary
- Reviewed all 13 deferred Sprint 20 issues
- Created `DEFERRED_ISSUES_TRIAGE.md` with per-issue do/defer recommendation
- Identified overlap map with Sprint 21 Priorities 1–3
- Verified Known Unknowns 4.1, 4.2, 4.3 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] All 13 deferred issues reviewed
- [ ] Each issue categorized as "Do in Sprint 21" or "Defer"
- [ ] Overlaps with Sprint 21 priorities identified
- [ ] All 3 Category 4 unknowns have verification results
- [ ] PREP_PLAN.md Task 5 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 6: Analyze Solve-Match Gap (17 Models)

````
On a new branch `planning/sprint21-task6` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 6: Analyze Solve-Match Gap (17 Models).

### OBJECTIVE

Identify the 17 models that solve but don't match (33 solve - 16 match = 17 gap) and classify the divergence causes. This directly supports Sprint 21 Priority 5 (match rate improvement, 16→20+).

### WHAT NEEDS TO BE DONE

1. **Extract the 17 non-matching solve-success models** from `data/gamslib/gamslib_status.json`
   - Note: models are a list of objects with `model_id`, `mcp_solve`, `solution_comparison` fields
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

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/SOLVE_MATCH_GAP_ANALYSIS.md` — per-model divergence analysis sorted by relative difference
- Top 5 near-match investigation findings with recommended fixes
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.1, 5.2, 5.3

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 5.1:** What is the primary divergence cause for the 17 solve-but-no-match models?
- Assumption: Primary cause is `.l` initialization differences → different local optima
- Verify by listing all 17 models with relative differences and convexity status

**Unknown 5.2:** Which near-match models (rel_diff < 1e-2) can be fixed with tolerance or initialization changes?
- Assumption: At least 4–6 models have rel_diff < 1e-2 and can be brought to match
- Verify by sorting models by rel_diff and testing tolerance adjustments

**Unknown 5.3:** Does the Sprint 20 `.l` emission work actually improve match rates?
- Assumption: `.l` initialization emission improves match rates for non-convex models
- Verify by checking how many solving models have `.l` values emitted

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 6 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Solve-match gap analyzed (17 models)" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 6: Analyze Solve-Match Gap - YYYY-MM-DD

**Branch:** `planning/sprint21-task6`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 6: Analyze Solve-Match Gap

- Created SOLVE_MATCH_GAP_ANALYSIS.md with 17-model divergence analysis
- Classified divergence causes and identified near-match models
- Verified Known Unknowns 5.1, 5.2, 5.3
- Updated PREP_PLAN.md Task 6 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 6: Analyze Solve-Match Gap (17 Models)" --body "$(cat <<'EOF'
## Summary
- Identified 17 non-matching solve-success models
- Classified divergence causes into categories (near-match, moderate, large, NaN)
- Investigated top 5 near-match models for specific causes
- Created `SOLVE_MATCH_GAP_ANALYSIS.md` with recommended fixes
- Verified Known Unknowns 5.1, 5.2, 5.3 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] All 17 models identified with objective value differences
- [ ] Models classified into divergence categories
- [ ] Top 5 near-match models investigated
- [ ] All 3 Category 5 unknowns have verification results
- [ ] PREP_PLAN.md Task 6 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 7: Audit semantic_undefined_symbol Models

````
On a new branch `planning/sprint21-task7` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 7: Audit semantic_undefined_symbol Models.

### OBJECTIVE

Determine whether the 7 `semantic_undefined_symbol` models are failing due to GAMSLIB source issues (models that reference undefined symbols intentionally) or nlp2mcp parser/IR bugs that can be fixed.

The resolution strategy depends entirely on whether these are source issues or bugs: source issues get documented and excluded from metrics; bugs get fixed.

### WHAT NEEDS TO BE DONE

1. **Get the list of 7 semantic_undefined_symbol models** from `data/gamslib/gamslib_status.json`
   - Note: models are a list of objects. Check `nlp2mcp_parse.error_category` or similar field for the category
2. **For each model, run** `parse_file()` and capture the undefined symbol name and context
3. **Check the original GAMS source** for each undefined symbol:
   - Is it defined in a `$include` file? → Cannot fix without `$include` support
   - Is it defined in a conditional block (`$if`/`$ifi`)? → May be fixable with macro expansion
   - Is it a GAMSLIB source error? → Document and exclude
   - Is it an nlp2mcp parser bug (symbol defined but not captured)? → Fix
4. **Classify each model** and write findings

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/SEMANTIC_ERROR_AUDIT.md` — per-model findings with classification
- Clear recommendation: fix vs. document-and-exclude for each model
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 6.1, 6.2

### KNOWN UNKNOWNS TO VERIFY

You MUST verify these unknowns and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

For each unknown below, update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 6.1:** Are the 7 semantic_undefined_symbol models caused by `$include` references?
- Assumption: Most of the 7 models reference symbols from `$include` files
- Verify by running each model, capturing undefined symbol, and checking for `$include`

**Unknown 6.2:** Should semantic_undefined_symbol models be excluded from pipeline metrics?
- Assumption: `$include`-dependent models should be reclassified as "unsupported"
- Verify by determining fixable vs. unsupported count from Unknown 6.1 results

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 7 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Semantic error models audited (7 models)" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 7: Audit semantic_undefined_symbol Models - YYYY-MM-DD

**Branch:** `planning/sprint21-task7`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 7: Audit semantic_undefined_symbol Models

- Created SEMANTIC_ERROR_AUDIT.md with 7-model classification
- Determined fixable vs. exclude recommendation for each model
- Verified Known Unknowns 6.1, 6.2
- Updated PREP_PLAN.md Task 7 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 7: Audit semantic_undefined_symbol Models" --body "$(cat <<'EOF'
## Summary
- Audited 7 `semantic_undefined_symbol` models
- Classified each as fixable (parser bug) or exclude (`$include`/source issue)
- Created `SEMANTIC_ERROR_AUDIT.md` with per-model findings
- Verified Known Unknowns 6.1, 6.2 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] All 7 models identified and analyzed
- [ ] Root cause classified for each model
- [ ] Fix vs. exclude recommendation for each
- [ ] Both Category 6 unknowns have verification results
- [ ] PREP_PLAN.md Task 7 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 8: Snapshot Baseline Metrics & Pipeline Retest

````
On a new branch `planning/sprint21-task8` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 8: Snapshot Baseline Metrics & Pipeline Retest.

### OBJECTIVE

Run the full pipeline test and snapshot baseline metrics at the start of Sprint 21 prep. This establishes the ground truth against which Sprint 21 progress will be measured.

### WHAT NEEDS TO BE DONE

1. **Run full test suite:** `make test` — verify all tests pass, record count
2. **Run full pipeline retest:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
3. **Record all metrics:**
   - Parse: X/160
   - Translate: X/Y
   - Solve: X
   - Match: X
   - Tests: X passed, X skipped, X xfailed
   - Error categories: lexer_invalid_char, internal_error, semantic_undefined_symbol, parser_invalid_expression, model_no_objective_def, etc.
4. **Compare with Sprint 20 retrospective values** — confirm consistency:
   - Expected: parse 132/160, translate 120/132, solve 33, match 16, tests 3,715
5. **Write baseline document** with commit hash, date, and all metrics

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md` — snapshot with commit hash, date, and all pipeline metrics
- Confirmation that Sprint 20 retrospective values match current state
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknown 8.1

### KNOWN UNKNOWNS TO VERIFY

You MUST verify this unknown and update `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md`:

Update its "Verification Results" section:
- Change `🔍 **Status:** INCOMPLETE` to either `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add a "Findings" subsection with evidence, data, and decisions

**Unknown 8.1:** How many models fail with `path_solve_terminated` vs. other PATH failure modes?
- Assumption: Among 88 solve failures, classify into `path_solve_terminated`, `path_syntax_error`, and translation failures
- Verify by classifying all solve-stage failures from pipeline retest output

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 8 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Baseline metrics snapshotted and verified" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 8: Snapshot Baseline Metrics & Pipeline Retest - YYYY-MM-DD

**Branch:** `planning/sprint21-task8`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

Run the full quality gate to confirm baseline:
```bash
make typecheck && make lint && make format && make test
```
All must pass. Record test count from `make test` output.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 8: Snapshot Baseline Metrics

- Created BASELINE_METRICS.md with full pipeline snapshot
- Confirmed Sprint 20 retrospective values match current state
- Verified Known Unknown 8.1
- Updated PREP_PLAN.md Task 8 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 8: Snapshot Baseline Metrics & Pipeline Retest" --body "$(cat <<'EOF'
## Summary
- Ran full test suite and pipeline retest
- Created `BASELINE_METRICS.md` with commit hash, date, and all metrics
- Confirmed Sprint 20 retrospective values match current state
- Verified Known Unknown 8.1 in `KNOWN_UNKNOWNS.md`

## Test plan
- [ ] Full test suite passes (3,715+ tests)
- [ ] Pipeline retest completed
- [ ] All metric categories recorded
- [ ] Values compared with Sprint 20 retrospective
- [ ] Unknown 8.1 has verification results
- [ ] PREP_PLAN.md Task 8 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 9: Review Sprint 20 Retrospective Action Items

````
On a new branch `planning/sprint21-task9` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 9: Review Sprint 20 Retrospective Action Items.

### OBJECTIVE

Review the Sprint 20 retrospective to ensure all action items and process recommendations are captured in Sprint 21 planning.

### WHAT NEEDS TO BE DONE

1. **Read Sprint 20 retrospective** (`docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md`):
   - Lines 300–362: Sprint 21 technical recommendations
   - Lines 351–361: Process recommendations (5 items)
   - Lines 365–381: Final metrics
   - Lines 383–440: What Went Well / What Could Be Improved / What We'd Do Differently
2. **Extract all action items** (explicit and implied)
3. **Map each action item** to Sprint 21 plan or prep task:
   - Already captured → note as "addressed"
   - Not captured → add to Sprint 21 plan or create new prep task
4. **Verify process recommendations** (5 items) are reflected in Sprint 21 working practices
5. **Document mapping** in brief alignment document

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/RETROSPECTIVE_ALIGNMENT.md` — mapping of Sprint 20 action items to Sprint 21 plan
- Confirmation that all critical action items are addressed

### KNOWN UNKNOWNS TO VERIFY

Task 9 has no specific unknowns assigned (it covers process alignment). However, review all unknowns and note if any retrospective action items create new unknowns that should be added to `KNOWN_UNKNOWNS.md`.

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 9 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Sprint 20 retrospective action items confirmed" in the Success Criteria section

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 9: Review Sprint 20 Retrospective Action Items - YYYY-MM-DD

**Branch:** `planning/sprint21-task9`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a research/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 9: Review Sprint 20 Retrospective

- Created RETROSPECTIVE_ALIGNMENT.md mapping action items to Sprint 21 plan
- Confirmed all 5 process recommendations are addressed
- Updated PREP_PLAN.md Task 9 status to COMPLETE
- Updated CHANGELOG.md
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 9: Review Sprint 20 Retrospective Action Items" --body "$(cat <<'EOF'
## Summary
- Reviewed Sprint 20 retrospective and extracted all action items
- Created `RETROSPECTIVE_ALIGNMENT.md` mapping items to Sprint 21 plan
- Confirmed all 5 process recommendations are reflected in Sprint 21 practices

## Test plan
- [ ] All action items extracted from retrospective
- [ ] Each mapped to Sprint 21 plan or identified as gap
- [ ] All 5 process recommendations confirmed
- [ ] Alignment document created
- [ ] PREP_PLAN.md Task 9 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````

---

## Task 10: Plan Sprint 21 Detailed Schedule

````
On a new branch `planning/sprint21-task10` (branched from `planning/sprint21-prep`), execute Sprint 21 Prep Task 10: Plan Sprint 21 Detailed Schedule.

IMPORTANT: This task depends on ALL tasks (1–9). Ensure all prior task PRs have been merged into `planning/sprint21-prep` before starting. If not all are merged, branch from the most current state that includes Tasks 2–9 deliverables.

### OBJECTIVE

Create the detailed day-by-day Sprint 21 execution plan incorporating all prep research, catalogs, and design documents.

Sprint 21 has 46–68h of work across 9 workstreams. Sprint 21 acceptance criteria: parse ≥135/160, lexer_invalid_char ≤5, internal_error ≤3, solve ≥36, match ≥20.

### WHAT NEEDS TO BE DONE

1. **Review all prep task outputs** (Tasks 1–9 deliverables):
   - `KNOWN_UNKNOWNS.md` — 27 unknowns with verification results
   - `MACRO_EXPANSION_DESIGN.md` — macro subsystem architecture
   - `INTERNAL_ERROR_CATALOG.md` — 7-model root cause catalog
   - `PATH_SYNTAX_ERROR_CATALOG.md` — 45-model root cause catalog
   - `DEFERRED_ISSUES_TRIAGE.md` — 13-issue do/defer categorization
   - `SOLVE_MATCH_GAP_ANALYSIS.md` — 17-model divergence analysis
   - `SEMANTIC_ERROR_AUDIT.md` — 7-model fix/exclude classification
   - `BASELINE_METRICS.md` — current pipeline snapshot
   - `RETROSPECTIVE_ALIGNMENT.md` — action item mapping
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

### DELIVERABLES

- `docs/planning/EPIC_4/SPRINT_21/PLAN.md` — detailed day-by-day schedule with workstream assignments
- `docs/planning/EPIC_4/SPRINT_21/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- Sprint 21 sprint log template: `docs/planning/EPIC_4/SPRINT_21/SPRINT_LOG.md`

### KNOWN UNKNOWNS TO VERIFY

Task 10 integrates all verified unknowns from Tasks 2–9 into the data-driven schedule. No new unknowns to verify, but confirm that all Critical/High unknowns from `KNOWN_UNKNOWNS.md` have been resolved (status ✅ or ❌) and that the schedule accounts for any unknowns marked ❌ WRONG.

### UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_21/PREP_PLAN.md`:
1. Change Task 10 status from `:large_blue_circle: NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with a bullet list of what was done
3. Fill in the "Result" section with a summary paragraph
4. Check off ALL acceptance criteria (change `- [ ]` to `- [x]`)
5. Check off "Sprint 21 detailed schedule created" in the Success Criteria section
6. Verify ALL 10 Success Criteria checkboxes are now checked — if so, add a note: "All prep tasks complete. Ready for Sprint 21 Day 1."

### UPDATE CHANGELOG.md

Add an entry under `## [Unreleased]` (after the most recent prep task entry):

```
### Sprint 21 Prep Task 10: Plan Sprint 21 Detailed Schedule - YYYY-MM-DD

**Branch:** `planning/sprint21-task10`

#### Summary
[1-2 sentence summary]

#### Activities
- [bullet list of activities]
```

### QUALITY GATE

This is a planning/documentation task — no code changes expected. Skip `make typecheck && make lint && make format && make test`.

### COMMIT

Commit all changes with this message format (DO NOT include Co-authored-by):
```
Complete Sprint 21 Prep Task 10: Plan Sprint 21 Detailed Schedule

- Created PLAN.md with day-by-day Sprint 21 schedule
- Created PLAN_PROMPTS.md with execution prompts for each day
- Created SPRINT_LOG.md template
- Updated PREP_PLAN.md Task 10 status to COMPLETE
- Updated CHANGELOG.md
- All 10 prep tasks complete
```

### PULL REQUEST

After committing and pushing, create a Pull Request:
```bash
gh pr create --base planning/sprint21-prep --title "Sprint 21 Prep Task 10: Plan Sprint 21 Detailed Schedule" --body "$(cat <<'EOF'
## Summary
- Created `PLAN.md` with day-by-day Sprint 21 schedule covering all 9 workstreams
- Created `PLAN_PROMPTS.md` with execution prompts for each day
- Created `SPRINT_LOG.md` template for daily progress tracking
- Incorporates findings from all prep Tasks 1–9
- All 10 prep tasks now complete — Sprint 21 ready for Day 1

## Test plan
- [ ] Day-by-day schedule covers entire sprint
- [ ] All 9 workstreams assigned to specific days
- [ ] Time estimates sum to 46–68h total
- [ ] Dependencies documented between days
- [ ] Checkpoint gates defined
- [ ] Execution prompts created for each day
- [ ] Sprint log template created
- [ ] All PREP_PLAN.md Success Criteria checked
EOF
)"
```

Then wait for reviewer comments. When comments arrive, fetch them with:
```bash
gh api repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments
```
Fix issues, commit, push, and reply to each comment using:
```bash
gh api "repos/jeffreyhorn/nlp2mcp/pulls/PULL_NUMBER/comments/COMMENT_ID/replies" -X POST -f body="..."
```
````
