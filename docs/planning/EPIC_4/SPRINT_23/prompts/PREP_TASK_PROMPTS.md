# Sprint 23 Preparation Task Prompts

**Purpose:** Step-by-step execution prompts for Sprint 23 Prep Tasks 2-10. Each prompt includes the full task objective, deliverables, Known Unknowns verification, PREP_PLAN.md updates, CHANGELOG.md updates, quality gate, and commit/PR instructions.

**Usage:** Copy the prompt for the task you are executing into a new Claude Code session.

---

## Prep Task 2: Triage path_solve_terminated Models (10)

**Branch:** `planning/sprint23-task2`

You are executing **Prep Task 2** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task2` (create from `planning/sprint23-prep`).

### Objective

Classify all 10 path_solve_terminated models by root cause to identify which are fixable in Sprint 23 and which require deeper architectural work or PATH author consultation.

### Background

- 10 models remain: dyncge, elec, etamac, fawley, gtm, maxmin, qsambal, rocket, sambal, twocge
- Key issues: #862 (sambal), #983 (elec)
- Sprint 22 WS2 fixed 4 models (fdesign, trussm, springchain, whouse) in ~12h; fawley remains path_solve_terminated
- Sprint 21 PATH convergence analysis showed most terminated models have pre-solver issues, not PATH convergence

### What Needs to Be Done

1. **For each of the 10 models, run MCP generation and attempt solve:**
   ```bash
   python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/<model>_mcp.gms
   # Then run with GAMS if available to capture PATH output
   ```
2. **Classify root cause into one of:**
   - **A: MCP pairing error** — wrong variable/equation pairing; fix in KKT builder or emitter
   - **B: Execution error** — division by zero, NA values, domain errors; fix in emitter or starting points
   - **C: PATH convergence** — genuine solver failure; may need reformulation or PATH author consultation
   - **D: Pre-solver infeasibility** — PATH detects infeasibility before iteration; likely KKT formulation bug
3. **For each model, record:** Root cause category (A/B/C/D), specific error message, estimated fix effort (hours), dependencies, relevant GitHub issue number
4. **Rank models by fix leverage** — prioritize models that also improve match count
5. **Create triage document:** `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` with root cause classification for all 10 models
- Ranked fix priority list with effort estimates
- Recommendation: which 5+ models to target in Sprint 23
- Verification results for KU-01, KU-02, KU-03, KU-04, KU-05 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-01** (Critical): Are the 10 models mostly MCP pairing/execution errors, not PATH convergence?
- **KU-02** (Critical): Is fixing 5+ models achievable in Sprint 23 timeframe?
- **KU-03** (High): Do sambal/qsambal dollar-condition issues require #1112 first?
- **KU-04** (High): Are dyncge/twocge CGE models structurally incompatible like orani?
- **KU-05** (High): Will fixing path_solve_terminated cascade models to model_infeasible?

For each unknown, replace the existing `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with one of:
- `**Verification Results:** ✅ VERIFIED — <brief finding>`
- `**Verification Results:** ❌ REFUTED — <brief finding>`
- `**Verification Results:** ⚠️ PARTIALLY CONFIRMED — <brief finding>`

Also update the Appendix C verification status tracking table with date, result, and action taken.

### Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md` Task 2:

1. Change status from `:large_blue_circle: NOT STARTED` to `:white_check_mark: COMPLETE`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with a summary of findings
4. Check off all acceptance criteria that are met:
   - [ ] All 10 models attempted (MCP generation + solve)
   - [ ] Each model classified as A (pairing), B (execution), C (convergence), or D (pre-solver)
   - [ ] Error messages captured for each model
   - [ ] Fix effort estimated per model
   - [ ] Top 5+ highest-leverage models identified
   - [ ] Triage document created
   - [ ] KU-01, KU-02, KU-03, KU-04, KU-05 verification results recorded in KNOWN_UNKNOWNS.md

### Update CHANGELOG.md

Add a bullet under the `### Sprint 23 Preparation` section in `CHANGELOG.md`:
```
- Complete Prep Task 2: Triage 10 path_solve_terminated models — classify root causes, rank fix priority, verify KU-01–KU-05
```

### Quality Gate

This is a research/documentation task — no code changes expected. If any code changes are made, run:
```bash
make typecheck && make lint && make format && make test
```

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 2: Triage path_solve_terminated models

- Create TRIAGE_PATH_SOLVE_TERMINATED.md with root cause classification for all 10 models
- Classify each as MCP pairing (A), execution error (B), PATH convergence (C), or pre-solver (D)
- Rank fix priority with effort estimates
- Verify KU-01, KU-02, KU-03, KU-04, KU-05 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 2 status to COMPLETE"
git push -u origin planning/sprint23-task2
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 2: Triage path_solve_terminated models" --body "$(cat <<'EOF'
## Summary
- Triage all 10 path_solve_terminated models by root cause (A: pairing, B: execution, C: convergence, D: pre-solver)
- Rank fix priority with effort estimates for Sprint 23 Priority 1
- Verify 5 Known Unknowns (KU-01–KU-05)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md`
- Updated `KNOWN_UNKNOWNS.md` with KU-01–KU-05 verification results
- Updated `PREP_PLAN.md` Task 2 marked COMPLETE

## Test plan
- [ ] Triage document covers all 10 models
- [ ] Each model has root cause classification and effort estimate
- [ ] KU verification results are complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 2 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 3: Triage model_infeasible Models (12)

**Branch:** `planning/sprint23-task3`

You are executing **Prep Task 3** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task3` (create from `planning/sprint23-prep`).

### Objective

Classify all 12 in-scope model_infeasible models by root cause to identify which are KKT formulation bugs (fixable) versus inherent MCP incompatibilities (permanent exclusions).

### Background

- 12 in-scope models: bearing, chain, cpack, lnts, markov, mathopt3, pak, paperco, prolog, robustlp, sparta, spatequ
- 3 permanently excluded: feasopt1, iobalance, orani
- Key issues: #1049 (pak), #1070 (prolog), #1081 (sparta), #1110 (markov), #1038 (spatequ)
- Sprint 22 WS3 fixed whouse, ibm1, uimp, mexss, pdi via sameas guard refactor and other KKT fixes
- Sprint 22 deferred decision doc: `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`

### What Needs to Be Done

1. **For each of the 12 models, run MCP generation and capture PATH output:**
   ```bash
   python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/<model>_mcp.gms
   ```
2. **Classify root cause:**
   - **A: KKT formulation bug** — incorrect stationarity, missing multiplier terms, wrong signs
   - **B: Structural infeasibility** — PATH preprocessor detects infeasibility (MODEL STATUS 4)
   - **C: Inherent MCP incompatibility** — model class (CGE, multi-solve, etc.) doesn't convert cleanly
   - **D: Missing feature** — requires grammar/IR feature not yet implemented
3. **For models with filed issues (#1049, #1070, #1081, #1110, #1038), review issue description for root cause clues**
4. **Estimate fix effort per model and identify dependencies**
5. **Recommend which models to target** (Category A/B are highest leverage; C may be permanent exclusions)
6. **Create triage document:** `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` with root cause classification for all 12 models
- Gross fix candidates vs. likely permanent exclusions
- Recommendation: which 4+ models to target in Sprint 23
- Verification results for KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-06** (Critical): Are 12 in-scope models primarily KKT formulation bugs?
- **KU-07** (High): Does Sprint 22 sameas guard pattern extend to pak, spatequ, sparta?
- **KU-08** (Critical): Is model_infeasible influx from other fixes manageable (≤ 3)?
- **KU-09** (Medium): Are chain/rocket genuinely non-convex infeasibility (not KKT bugs)?
- **KU-10** (High): Is markov multi-pattern Jacobian (#1110) fixable in 3-4h?
- **KU-11** (Medium): Is prolog CES demand singular Jacobian addressable?

For each unknown, replace the existing `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with `**Verification Results:** ✅ VERIFIED — ...`, `❌ REFUTED — ...`, or `⚠️ PARTIALLY CONFIRMED — ...`. Also update Appendix C.

### Update PREP_PLAN.md

Update `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md` Task 3:
1. Change status to `:white_check_mark: COMPLETE`
2. Fill in **Changes** and **Result** sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 3: Triage 12 model_infeasible models — classify root causes, identify fix candidates vs. permanent exclusions, verify KU-06–KU-11
```

### Quality Gate

Research/documentation task. If any code changes: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 3: Triage model_infeasible models

- Create TRIAGE_MODEL_INFEASIBLE.md with root cause classification for all 12 models
- Classify each as KKT bug (A), structural (B), incompatible (C), or missing feature (D)
- Identify gross fix candidates vs. permanent exclusions
- Verify KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 3 status to COMPLETE"
git push -u origin planning/sprint23-task3
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 3: Triage model_infeasible models" --body "$(cat <<'EOF'
## Summary
- Triage all 12 in-scope model_infeasible models by root cause
- Identify gross fix candidates vs. permanent exclusions for Sprint 23 Priority 2
- Verify 6 Known Unknowns (KU-06–KU-11)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md`
- Updated `KNOWN_UNKNOWNS.md` with KU-06–KU-11 verification results
- Updated `PREP_PLAN.md` Task 3 marked COMPLETE

## Test plan
- [ ] Triage document covers all 12 models
- [ ] Each model has root cause classification and effort estimate
- [ ] KU verification results are complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 3 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 4: Investigate Alias-Aware Differentiation (#1111)

**Branch:** `planning/sprint23-task4`

You are executing **Prep Task 4** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task4` (create from `planning/sprint23-prep`).

### Objective

Research the alias-aware differentiation architectural change needed for Sprint 23 Priority 3. Determine scope of impact, design approach, and regression risk before implementation.

### Background

- GitHub Issue: #1111 (AD engine: alias-aware differentiation with summation-context tracking)
- Sprint 22 KU-27: Discovered Day 11, deferred to Sprint 23
- Related research: `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`
- AD engine: `src/ad/` (gradient computation, Jacobian computation)
- Current behavior: AD engine treats aliased set indices as independent, producing incorrect derivatives when the same physical index is referenced through different alias names
- Sprint 22 naive fix was attempted and **reverted** because it added spurious `sameas` guards in summation contexts where aliased indices are independent iteration variables (regression in dispatch model)

### What Needs to Be Done

1. **Read Issue #1111 fully** — understand the specific failure case and proposed fix
2. **Identify affected models** — which of the 42 mismatch models are affected by alias issues?
   ```bash
   grep -il "alias" data/gamslib/raw/*.gms | head -20
   ```
3. **Map the AD pipeline** — trace how set indices flow through `src/ad/`, `src/kkt/stationarity.py`, `src/emit/`
4. **Design the fix** — document where alias resolution should happen, what "summation-context tracking" means concretely, how to detect aliased indices, regression safeguards
5. **Identify test models** — find 2-3 models that demonstrate the bug and will verify the fix
6. **Estimate regression risk** — how many currently-solving models use aliases?

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` with root cause analysis, affected models list, proposed fix design with code locations, regression risk assessment, test plan
- Verification results for KU-12, KU-13, KU-15, KU-16, KU-17 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-12** (Critical): Can alias-aware differentiation be implemented without regression? (Sprint 22 naive fix regressed dispatch)
- **KU-13** (High): Does the alias fix only affect alias-using models (selectivity)?
- **KU-15** (High): Are alias and dollar-condition fixes independent (no coupling)?
- **KU-16** (Medium): Is the non-convex multi-KKT divergence population irreducible (~12 models)?
- **KU-17** (High): Are verified-convex mismatch models fixable (guaranteed matches if KKT bugs fixed)?

For each, replace the `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with the appropriate status (✅ VERIFIED/❌ REFUTED/⚠️ PARTIALLY CONFIRMED). Also update Appendix C.

### Update PREP_PLAN.md

Update Task 4: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 4: Investigate alias-aware differentiation (#1111) — design fix with summation-context tracking, assess regression risk, verify KU-12/KU-13/KU-15–KU-17
```

### Quality Gate

Research/documentation task. If any code changes: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 4: Investigate alias-aware differentiation

- Create DESIGN_ALIAS_DIFFERENTIATION.md with root cause analysis and fix design
- Trace AD pipeline for alias handling; design summation-context tracking
- Identify affected models and assess regression risk
- Verify KU-12, KU-13, KU-15, KU-16, KU-17 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 4 status to COMPLETE"
git push -u origin planning/sprint23-task4
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 4: Investigate alias-aware differentiation (#1111)" --body "$(cat <<'EOF'
## Summary
- Research alias-aware differentiation architectural change for Sprint 23 Priority 3
- Design summation-context tracking to distinguish alias-via-same-variable from independent iteration
- Identify affected models and assess regression risk
- Verify 5 Known Unknowns (KU-12, KU-13, KU-15, KU-16, KU-17)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`
- Updated `KNOWN_UNKNOWNS.md` with verification results
- Updated `PREP_PLAN.md` Task 4 marked COMPLETE

## Test plan
- [ ] Design document includes regression risk assessment
- [ ] Affected models identified (both failing and passing)
- [ ] 2-3 test models identified for verification
- [ ] KU verification results complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 4 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 5: Investigate Dollar-Condition Propagation (#1112)

**Branch:** `planning/sprint23-task5`

You are executing **Prep Task 5** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task5` (create from `planning/sprint23-prep`).

### Objective

Research the dollar-condition propagation architectural change needed for Sprint 23 Priority 3. Determine where conditions are lost in the AD pipeline and design the propagation mechanism.

### Background

- GitHub Issue: #1112 (KKT: Dollar-condition propagation through AD/stationarity pipeline)
- Sprint 22 KU-28: Discovered Day 12, deferred to Sprint 23
- Dollar conditions in GAMS: `expr$condition` or `$(condition)` syntax
- `condition` rule in grammar: `DOLLAR (paren|bracket|cond_bound|ref_indexed|NUMBER|ID)`
- AD engine preserves `DollarConditional` nodes during differentiation (returns `(df/dx)$cond`), but condition propagation/collection into KKT/stationarity domains is incomplete — objective-gradient scanning and stationarity emission lose these conditions
- Stationarity equations need condition guards to match the original model's conditional structure
- Concrete fix path proposed in Sprint 22 KU-28: Add `_extract_gradient_conditions()` to `src/ad/gradient.py`, store in `KKTSystem.gradient_conditions`, check in `_find_variable_access_condition()` in stationarity.py

### What Needs to Be Done

1. **Read Issue #1112 fully** — understand the specific failure case and examples
2. **Trace dollar conditions through the pipeline:** IR representation (`DollarConditional` AST node?), `src/ad/` encounters during differentiation, propagation to stationarity equations, appearance in emitted MCP
3. **Identify affected models** — which mismatch models use dollar conditions in objectives, constraint definitions, or other expressions that feed AD/stationarity?
4. **Design the propagation mechanism:** metadata on derivative expressions, gradient/Jacobian condition annotations, combining multiple nested conditions
5. **Assess interaction with Task 4** (alias differentiation) — are the two changes independent or coupled?
6. **Estimate regression risk** — dollar conditions are pervasive in GAMS models

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md` with dollar-condition representation in IR, pipeline trace showing where conditions are lost, proposed propagation mechanism, interaction analysis with #1111, regression risk assessment, test plan
- Verification results for KU-14, KU-15 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-14** (High): Does dollar-condition propagation require changes to gradient only, or also Jacobian?
- **KU-15** (High): Are dollar-condition and alias fixes independent (no coupling)? *(Also verified in Task 4 — cross-check findings)*

For each, replace the `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with the appropriate status (✅ VERIFIED/❌ REFUTED/⚠️ PARTIALLY CONFIRMED). Also update Appendix C.

### Update PREP_PLAN.md

Update Task 5: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 5: Investigate dollar-condition propagation (#1112) — design propagation mechanism, assess interaction with alias differentiation, verify KU-14/KU-15
```

### Quality Gate

Research/documentation task. If any code changes: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 5: Investigate dollar-condition propagation

- Create DESIGN_DOLLAR_CONDITION_PROPAGATION.md with pipeline trace and propagation design
- Trace DollarConditional through IR → AD → KKT → Emit pipeline
- Design condition extraction and storage mechanism
- Assess interaction with alias differentiation (#1111)
- Verify KU-14, KU-15 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 5 status to COMPLETE"
git push -u origin planning/sprint23-task5
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 5: Investigate dollar-condition propagation (#1112)" --body "$(cat <<'EOF'
## Summary
- Research dollar-condition propagation architectural change for Sprint 23 Priority 3
- Trace where dollar conditions are lost in the AD pipeline
- Design propagation mechanism with condition extraction and storage
- Assess interaction with alias differentiation (#1111)
- Verify 2 Known Unknowns (KU-14, KU-15)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md`
- Updated `KNOWN_UNKNOWNS.md` with verification results
- Updated `PREP_PLAN.md` Task 5 marked COMPLETE

## Test plan
- [ ] Design document traces dollar conditions through full pipeline
- [ ] Interaction with alias differentiation assessed
- [ ] Affected models identified
- [ ] KU verification results complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 5 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 6: Triage path_syntax_error Subcategories G+B

**Branch:** `planning/sprint23-task6`

You are executing **Prep Task 6** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task6` (create from `planning/sprint23-prep`).

### Objective

Identify the specific models in path_syntax_error subcategories G (set index reuse, 2 models) and B (domain violations, 5 models), verify root causes, and estimate fix effort for each.

### Background

- 20 path_syntax_error models remain overall; Priority 4 targets the 7-model G+B subset
- Subcategory G (set index reuse): 2 models — need aliasing or index renaming
- Subcategory B (domain violations): 5 models — need domain conditioning fixes
- Key issues: #956 (nonsharp), #1041 (cesam2), #882/#871 (camcge)
- Sprint 22 KU-03 refuted common-bug assumption for subcategory B — "original 5 models dispersed; current B is cesam/cesam2 (new)"
- Sprint 22 KU-04 verified aliasing mechanism is sound for subcategory G but detection needs enhancement

### What Needs to Be Done

1. **Identify the specific 7 models** by running the pipeline on all 20 path_syntax_error models and categorizing the error type
2. **For subcategory G models (2):** Examine set index reuse patterns, verify Sprint 22 KU-04 finding, estimate fix effort
3. **For subcategory B models (5):** Note Sprint 22 KU-03 finding (NOT a single emitter bug), classify each model's specific domain violation, review #956, #1041, #882/#871 for details, estimate fix effort per model
4. **Check for overlap** — do any G+B models also appear in path_solve_terminated or model_infeasible lists?
5. **Create ranked fix list** with dependencies
6. **Create triage document:** `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` with named list of all 7 G+B models, per-model root cause and error details, fix effort estimates, cross-reference with existing issues
- Verification results for KU-18, KU-19, KU-20, KU-21 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-18** (High): Does subcategory G aliasing mechanism work for remaining 2 models? (Sprint 22 KU-04 carryforward)
- **KU-19** (High): Do subcategory B (5 models) have diverse root causes? (Sprint 22 KU-03 carryforward)
- **KU-20** (High): Will fixing 5 path_syntax_error models inflate model_infeasible?
- **KU-21** (Medium): Are new Sprint 22 subcategories (K, GUSS, hyphenated labels) low-effort?

For each, replace the `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with the appropriate status (✅ VERIFIED/❌ REFUTED/⚠️ PARTIALLY CONFIRMED). Also update Appendix C.

### Update PREP_PLAN.md

Update Task 6: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 6: Triage path_syntax_error subcategories G+B — classify 7 models, estimate fix effort, verify KU-18–KU-21
```

### Quality Gate

Research/documentation task. If any code changes: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 6: Triage path_syntax_error G+B

- Create TRIAGE_PATH_SYNTAX_ERROR_GB.md with per-model root cause for 7 G+B models
- Classify subcategory G (set index reuse) and B (domain violations) separately
- Estimate fix effort and check cross-category overlap
- Verify KU-18, KU-19, KU-20, KU-21 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 6 status to COMPLETE"
git push -u origin planning/sprint23-task6
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 6: Triage path_syntax_error subcategories G+B" --body "$(cat <<'EOF'
## Summary
- Triage 7 path_syntax_error models in subcategories G (set index reuse) and B (domain violations)
- Per-model root cause classification and fix effort estimates
- Check cross-category overlap with path_solve_terminated and model_infeasible
- Verify 4 Known Unknowns (KU-18–KU-21)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md`
- Updated `KNOWN_UNKNOWNS.md` with KU-18–KU-21 verification results
- Updated `PREP_PLAN.md` Task 6 marked COMPLETE

## Test plan
- [ ] All 7 G+B models identified by name
- [ ] Each model's specific error pattern documented
- [ ] Fix effort estimated per model
- [ ] KU verification results complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 6 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 7: Catalog and Classify Translate Failures (15)

**Branch:** `planning/sprint23-task7`

You are executing **Prep Task 7** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task7` (create from `planning/sprint23-prep`).

### Objective

Catalog all 15 translate failures, classify them as compilation errors vs. timeouts, and identify the highest-leverage fixes for Sprint 23 Priority 5.

### Background

- 15 translate failures remain (141/156 = 90.4% translate rate)
- Mix of compilation errors and timeout issues
- Sprint 23 acceptance criterion: ≥ 93% of parsed models (≥ 145/156 assuming 156 parsed)
- Pipeline retest script: `.venv/bin/python scripts/gamslib/run_full_test.py`
- Related issues: #952 (lmp2 empty subsets), #953 (paperco loop body), #940 (mexls universal set), #1062 (tricp)

### What Needs to Be Done

1. **Run pipeline on all 156 parsed models and capture translate failures:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --only-translate --quiet 2>&1 | grep -Ei 'fail|error|timeout'
   ```
2. **For each failure, classify as:**
   - **A: Compilation error** — GAMS can't compile the MCP output; fix in emitter/translator
   - **B: Timeout** — Translation takes too long; may need recursion/complexity optimization
   - **C: Missing IR feature** — Model uses grammar constructs not yet in the IR
   - **D: Internal error** — Python exception during translation
3. **For compilation errors, capture the specific GAMS error message**
4. **Cross-reference with existing issues** (#952, #953, #940, #1062, etc.)
5. **Rank by fix effort** — quick compilation fixes first, then investigate timeouts
6. **Create catalog document:** `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md` with named list of all 15 failing models, classification, error messages, cross-reference with issues, ranked fix priority
- Verification results for KU-22, KU-23, KU-24, KU-25 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknowns from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-22** (High): Are compilation error fixes higher leverage than timeout fixes?
- **KU-23** (Medium): Are timeout models architecturally intractable (gastrans pattern)?
- **KU-24** (High): Are 4 compilation fixes sufficient to reach ≥ 145/156 translate target?
- **KU-25** (Medium): Do paperco (#953) and lmp2 (#952) loop-body issues share a common parser fix?

For each, replace the `**Verification Results:** 🔍 Status: INCOMPLETE` line in KNOWN_UNKNOWNS.md with the appropriate status (✅ VERIFIED/❌ REFUTED/⚠️ PARTIALLY CONFIRMED). Also update Appendix C.

### Update PREP_PLAN.md

Update Task 7: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 7: Catalog 15 translate failures — classify as compilation/timeout/missing feature/internal, rank fix priority, verify KU-22–KU-25
```

### Quality Gate

Research/documentation task. If any code changes: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 7: Catalog translate failures

- Create CATALOG_TRANSLATE_FAILURES.md with classification for all 15 failures
- Classify each as compilation error (A), timeout (B), missing feature (C), or internal error (D)
- Rank fix priority; identify top 4+ for Sprint 23 target
- Verify KU-22, KU-23, KU-24, KU-25 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 7 status to COMPLETE"
git push -u origin planning/sprint23-task7
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 7: Catalog translate failures" --body "$(cat <<'EOF'
## Summary
- Catalog all 15 translate failures with classification and error details
- Rank fix priority for Sprint 23 Priority 5 (target: 15 → ≤ 11)
- Verify 4 Known Unknowns (KU-22–KU-25)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md`
- Updated `KNOWN_UNKNOWNS.md` with KU-22–KU-25 verification results
- Updated `PREP_PLAN.md` Task 7 marked COMPLETE

## Test plan
- [ ] All 15 translate failures identified by name
- [ ] Each classified with error details
- [ ] Top 4+ highest-leverage fixes identified
- [ ] KU verification results complete in KNOWN_UNKNOWNS.md Appendix C
- [ ] PREP_PLAN.md Task 7 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 8: Run Full Pipeline Baseline (per PR6)

**Branch:** `planning/sprint23-task8`

You are executing **Prep Task 8** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task8` (create from `planning/sprint23-prep`).

### Objective

Establish the definitive Sprint 23 baseline using a full pipeline run (per Sprint 22 process recommendation PR6). This provides the starting metrics that all Sprint 23 progress is measured against.

### Background

- Sprint 22 final: parse 156/160, translate 141/156, solve 89/141, match 47/160
- Pipeline script: `.venv/bin/python scripts/gamslib/run_full_test.py`
- Status JSON: `data/gamslib/gamslib_status.json`
- PR6: Use full pipeline for all definitive metrics
- PR7: Track model_infeasible gross fixes and gross influx separately
- PR8: Use absolute counts alongside percentages for parse success

### What Needs to Be Done

1. **Run full pipeline** (all stages, no `--only-*` flags):
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
2. **Record all metrics per PR6/PR7/PR8:**
   - Parse: X/160 (Y%)
   - Translate: X/Y (Z% of parsed)
   - Solve: X (count) + X/Y (Z% of translated)
   - Match: X (count) + X/160 (Y% of corpus)
   - Error categories: path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license (counts)
   - model_infeasible breakdown: in-scope vs. permanently excluded
3. **Compare against Sprint 22 final metrics** to confirm no regressions since merge
4. **Save baseline metrics** for Sprint 23 checkpoint comparisons
5. **Create baseline document:** `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md` with full pipeline results, error category breakdown, comparison with Sprint 22, confirmation of no regressions
- Updated `data/gamslib/gamslib_status.json`
- Verification results for KU-26 in KNOWN_UNKNOWNS.md Appendix C

### Known Unknowns Verification

You MUST verify the following unknown from `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`:

- **KU-26** (Low): Are multi-solve incomparable classifications stable? (Sprint 22 KU-30 carryforward)

Update `**Verification Results:**` in KNOWN_UNKNOWNS.md and Appendix C.

### Update PREP_PLAN.md

Update Task 8: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 8: Run full pipeline baseline — establish Sprint 23 starting metrics per PR6/PR7/PR8, verify KU-26
```

### Quality Gate

No code changes expected. If any: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       data/gamslib/gamslib_status.json \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 8: Run full pipeline baseline

- Create BASELINE_METRICS.md with definitive Sprint 23 starting metrics
- Full pipeline run per PR6; metrics expressed per PR7/PR8
- Confirm no regressions vs Sprint 22 final metrics
- Update gamslib_status.json with fresh pipeline results
- Verify KU-26 in KNOWN_UNKNOWNS.md
- Update PREP_PLAN.md Task 8 status to COMPLETE"
git push -u origin planning/sprint23-task8
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 8: Full pipeline baseline" --body "$(cat <<'EOF'
## Summary
- Establish definitive Sprint 23 baseline with full pipeline run (per PR6)
- Record all metrics per PR6/PR7/PR8
- Confirm no regressions vs Sprint 22 final metrics
- Verify KU-26 (multi-solve incomparable classification stability)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md`
- Updated `data/gamslib/gamslib_status.json`
- Updated `KNOWN_UNKNOWNS.md` with KU-26 verification result
- Updated `PREP_PLAN.md` Task 8 marked COMPLETE

## Test plan
- [ ] Full pipeline run completed (no --only-* flags)
- [ ] All metrics recorded: parse, translate, solve, match, error categories
- [ ] model_infeasible split into in-scope and permanently excluded
- [ ] No regressions vs Sprint 22 final confirmed
- [ ] PREP_PLAN.md Task 8 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 9: Review Sprint 22 Retrospective Action Items

**Branch:** `planning/sprint23-task9`

You are executing **Prep Task 9** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task9` (create from `planning/sprint23-prep`).

### Objective

Verify that all Sprint 22 retrospective recommendations and action items are captured in Sprint 23 planning. Confirm nothing is missed.

### Background

- Sprint 22 Retrospective: `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
- Process recommendations: PR6 (full pipeline), PR7 (gross fixes/influx), PR8 (absolute counts)
- Sprint 22 deferred items: subcategories G+B, path_solve_terminated residual
- Sprint 23 section in PROJECT_PLAN.md: lines 629-740
- This task depends on Task 1 (Known Unknowns) and should cross-check KU verification results from Tasks 2-8

### What Needs to Be Done

1. **Read Sprint 22 Retrospective completely** — extract all action items and recommendations
2. **Map each item to Sprint 23 tasks or process changes:**

   | Sprint 22 Recommendation | Sprint 23 Action | Status |
   |--------------------------|------------------|--------|
   | PR6: Full pipeline for definitive metrics | Task 8 baseline + all checkpoints | Planned |
   | PR7: Gross fixes/influx tracking | Acceptance criteria + reporting | Planned |
   | PR8: Absolute counts for parse | Acceptance criteria + reporting | Planned |
   | WS1 G+B deferred | Priority 4 | Planned |
   | path_solve_terminated ≤ 5 | Priority 1 | Planned |
   | model_infeasible influx budget | Priority 2 + PR7 | Planned |
   | Full pipeline at checkpoints | Sprint 23 process | Planned |

3. **Identify any gaps** — items not captured in Sprint 23 planning
4. **Update Known Unknowns** (Task 1) if new risks found
5. **Cross-check all KU verification results from Tasks 2-8** for completeness
6. **Create alignment document:** `docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md`

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md` with mapping of all retrospective items to Sprint 23 actions, PR6/PR7/PR8 integration confirmation, gaps identified
- Cross-check of all KU verification results from Tasks 2-8

### Known Unknowns Verification

This task cross-checks ALL remaining KU verification results from Tasks 2-8. Verify that Appendix C in KNOWN_UNKNOWNS.md is complete — every KU assigned to Tasks 2-8 should have a verification result by now. Flag any that are still INCOMPLETE.

### Update PREP_PLAN.md

Update Task 9: status to COMPLETE, fill in Changes/Result, check off acceptance criteria.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 9: Review Sprint 22 retrospective — confirm all action items captured in Sprint 23 planning, verify PR6/PR7/PR8 integration
```

### Quality Gate

Research/documentation task. No code changes expected.

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md \
       docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 9: Review Sprint 22 retrospective

- Create RETROSPECTIVE_ALIGNMENT.md mapping all retrospective items to Sprint 23 actions
- Confirm PR6, PR7, PR8 integration into Sprint 23 process
- Cross-check all KU verification results from Tasks 2-8
- Update PREP_PLAN.md Task 9 status to COMPLETE"
git push -u origin planning/sprint23-task9
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 9: Review Sprint 22 retrospective" --body "$(cat <<'EOF'
## Summary
- Map all Sprint 22 retrospective recommendations to Sprint 23 actions
- Confirm PR6 (full pipeline), PR7 (gross/influx), PR8 (absolute counts) integration
- Cross-check all KU verification results from Tasks 2-8 for completeness
- Identify any gaps in Sprint 23 planning

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md`
- Updated `PREP_PLAN.md` Task 9 marked COMPLETE

## Test plan
- [ ] All retrospective "What Could Be Improved" items mapped
- [ ] All "What We'd Do Differently" items addressed
- [ ] PR6, PR7, PR8 confirmed in Sprint 23 process
- [ ] KU verification results cross-checked for completeness
- [ ] PREP_PLAN.md Task 9 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Prep Task 10: Plan Sprint 23 Detailed Schedule

**Branch:** `planning/sprint23-task10`

You are executing **Prep Task 10** from `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`. Work on branch `planning/sprint23-task10` (create from `planning/sprint23-prep`).

**Important:** This task depends on Tasks 1-9. All prep tasks should be complete before starting this one.

### Objective

Create detailed Sprint 23 plan with day-by-day schedule, checkpoints, and contingency plans, incorporating all findings from prep tasks.

### Background

- Sprint 23 in PROJECT_PLAN.md: `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 629-740
- Sprint 22 Plan format: `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (15-day schedule, 2 checkpoints)
- Sprint 22 Prompts: `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` (day-by-day execution)
- Estimated effort: 32-44 hours across 5 priorities
- 24 GitHub issues labeled `sprint-23`
- All prep task findings should be incorporated (Tasks 1-9 deliverables)

### What Needs to Be Done

1. **Read all prep task deliverables:**
   - Task 1: `KNOWN_UNKNOWNS.md` (risk mitigation schedule)
   - Task 2: `TRIAGE_PATH_SOLVE_TERMINATED.md` (Priority 1 day assignments)
   - Task 3: `TRIAGE_MODEL_INFEASIBLE.md` (Priority 2 day assignments)
   - Task 4: `DESIGN_ALIAS_DIFFERENTIATION.md` (Priority 3 implementation plan)
   - Task 5: `DESIGN_DOLLAR_CONDITION_PROPAGATION.md` (Priority 3 implementation plan)
   - Task 6: `TRIAGE_PATH_SYNTAX_ERROR_GB.md` (Priority 4 day assignments)
   - Task 7: `CATALOG_TRANSLATE_FAILURES.md` (Priority 5 day assignments)
   - Task 8: `BASELINE_METRICS.md` (starting metrics for checkpoints)
   - Task 9: `RETROSPECTIVE_ALIGNMENT.md` (process requirements)
2. **Create 15-day schedule (Day 0-14)** with day-by-day tasks, priority area, expected metrics improvements, integration risks
3. **Define 2 checkpoints:**
   - Checkpoint 1 (Day 5): Expected metrics, GO/CONDITIONAL GO/NO-GO criteria
   - Checkpoint 2 (Day 10): Expected metrics, GO/NO-GO criteria
4. **Create day-by-day prompts** for execution (following Sprint 22 format in `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md`)
5. **Define contingency plans** for high-risk areas (alias differentiation regressions, model_infeasible influx)
6. **Map 24 sprint-23 issues** to specific days
7. **Initialize sprint log**

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/PLAN.md` with sprint goals, 15-day schedule, 2 checkpoints with GO/NO-GO criteria, risk mitigation plan, issue-to-day mapping
- `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md` with day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` (initialized, empty)
- All KU verification results synthesized into risk mitigation schedule

### Known Unknowns Verification

This task synthesizes ALL KU verification results into the sprint plan. Ensure the risk mitigation schedule accounts for:
- Any REFUTED assumptions (adjust targets/schedule)
- Any PARTIALLY CONFIRMED findings (add contingency)
- All VERIFIED assumptions (confirm schedule is valid)

### Update PREP_PLAN.md

Update Task 10: status to COMPLETE, fill in Changes/Result, check off acceptance criteria. Also check off all items in the "Success Criteria for Prep Phase" section at the bottom.

### Update CHANGELOG.md

Add under `### Sprint 23 Preparation`:
```
- Complete Prep Task 10: Plan Sprint 23 detailed schedule — 15-day plan with 2 checkpoints, day-by-day prompts, issue mapping, contingency plans
```

### Quality Gate

No code changes expected. If any: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_23/PLAN.md \
       docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md \
       docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md \
       docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md \
       CHANGELOG.md
git commit -m "Complete Sprint 23 Prep Task 10: Plan detailed schedule

- Create PLAN.md with 15-day schedule, 2 checkpoints, and contingency plans
- Create PLAN_PROMPTS.md with day-by-day execution prompts
- Initialize SPRINT_LOG.md for Sprint 23 progress tracking
- Map all 24 sprint-23 issues to specific days
- Synthesize all prep task findings into coherent sprint plan
- Update PREP_PLAN.md Task 10 and overall success criteria to COMPLETE"
git push -u origin planning/sprint23-task10
```

### Create Pull Request

```bash
gh pr create --base planning/sprint23-prep --title "Sprint 23 Prep Task 10: Detailed schedule and day-by-day prompts" --body "$(cat <<'EOF'
## Summary
- Create Sprint 23 detailed plan with 15-day schedule (Day 0-14)
- Define 2 checkpoints with GO/NO-GO criteria
- Create day-by-day execution prompts
- Map all 24 sprint-23 issues to specific days
- Define contingency plans for alias differentiation regressions and model_infeasible influx
- Synthesize all prep task findings (Tasks 1-9) into risk mitigation schedule

## Deliverables
- `docs/planning/EPIC_4/SPRINT_23/PLAN.md`
- `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md`
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` (initialized)
- Updated `PREP_PLAN.md` Task 10 and overall success criteria marked COMPLETE

## Test plan
- [ ] Plan has 15-day schedule (Day 0 through Day 14)
- [ ] All 5 priority areas assigned to specific days
- [ ] 2 checkpoints defined with expected metrics and GO/NO-GO criteria
- [ ] Day-by-day prompts created
- [ ] All 24 sprint-23 issues mapped to days or backlog
- [ ] Contingency plans defined
- [ ] PR6/PR7/PR8 process requirements integrated
- [ ] Sprint log initialized
- [ ] PREP_PLAN.md Task 10 acceptance criteria all checked
EOF
)"
```

Then wait for reviewer comments before proceeding.

---

## Execution Order

The recommended execution order follows the critical path from `PREP_PLAN.md`:

```
Phase 1 (parallel): Task 8 (baseline)
Phase 2 (parallel): Tasks 2, 3, 4, 5, 6, 7
Phase 3 (sequential): Task 9 (after Tasks 2-8)
Phase 4 (sequential): Task 10 (after all above)
```

Task 1 (Known Unknowns) is already COMPLETE.

**Note:** Tasks 2-7 can be executed in parallel on separate branches. Tasks 9 and 10 must wait for all prior tasks.
