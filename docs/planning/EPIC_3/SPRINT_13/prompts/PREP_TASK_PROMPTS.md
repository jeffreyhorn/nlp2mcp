# Sprint 13 Prep Task Prompts

This document contains prompts for completing each prep task (Tasks 2-10) from `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`.

Each prompt includes:
1. Full task objectives and deliverables
2. Instructions for verifying associated Known Unknowns
3. Instructions for updating PREP_PLAN.md
4. Instructions for updating CHANGELOG.md
5. Quality gate requirements
6. Commit message format
7. PR creation instructions

---

## Task 2: Research GAMSLIB Structure and Access

### Prompt

```
On a new branch, complete Prep Task 2 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Research GAMSLIB Structure and Access.

## TASK OBJECTIVES

Research the structure, organization, and access methods for the GAMS Model Library to inform download script development.

## WHAT NEEDS TO BE DONE

1. **Explore GAMSLIB Web Interface (1 hour)**
   - Navigate https://www.gams.com/latest/gamslib_ml/libhtml/
   - Understand navigation structure (by type, alphabetical, etc.)
   - Identify model listing pages
   - Note URL patterns for individual models

2. **Analyze Model Page Structure (1 hour)**
   - Select 5-10 representative models
   - Document: URL structure, metadata displayed, download links
   - Check if .gms files are directly downloadable
   - Identify any authentication requirements

3. **Research GAMS Command-Line Access (1 hour)**
   - Check if `gamslib` command can extract models
   - Test: `gamslib trnsport` (transportation model)
   - Document command syntax and options
   - Compare web download vs command-line extraction

4. **Document Findings (30 min)**
   - Create research summary document
   - List URL patterns and access methods
   - Document any limitations or requirements
   - Recommend approach for download script

## DELIVERABLES

- `docs/research/GAMSLIB_ACCESS_RESEARCH.md` with:
  - GAMSLIB URL structure documentation
  - Model page metadata analysis
  - Access method comparison (web vs command-line)
  - Recommended approach for download script
- Test downloads of 3-5 sample models

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 1.1:** What is the URL structure for downloading individual GAMSLIB models?
- **Unknown 1.2:** Can the `gamslib` command-line tool extract models locally?
- **Unknown 1.3:** What metadata is available on GAMSLIB model pages?
- **Unknown 1.5:** Are there dependencies between GAMSLIB models ($include files)?
- **Unknown 1.6:** Is the GAMSLIB web structure stable or version-dependent?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add **Findings:** with detailed results
- Add **Evidence:** with specific examples, URLs, or command outputs
- Add **Decision:** with recommendation based on findings

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 2 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria:
   - [x] GAMSLIB web structure documented
   - [x] URL patterns for models identified
   - [x] Authentication requirements determined
   - [x] gamslib command-line tool evaluated
   - [x] Recommended download approach documented
   - [x] Sample models successfully downloaded
   - [x] Unknowns 1.1, 1.2, 1.3, 1.5, 1.6 verified and updated in KNOWN_UNKNOWNS.md

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md under the appropriate section:

```markdown
### Sprint 13 Prep

- **Task 2: Research GAMSLIB Structure and Access** - Completed GAMSLIB access research, documented URL patterns and metadata structure, evaluated gamslib command-line tool, verified 5 unknowns (1.1, 1.2, 1.3, 1.5, 1.6)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before proceeding.

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 2: Research GAMSLIB Structure and Access

- Created docs/research/GAMSLIB_ACCESS_RESEARCH.md with:
  - GAMSLIB URL structure documentation
  - Model page metadata analysis
  - Access method comparison (web vs command-line)
  - Recommended download approach
- Downloaded 3-5 sample models for testing
- Verified Unknowns 1.1, 1.2, 1.3, 1.5, 1.6 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 2 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 2: Research GAMSLIB Structure and Access" --body "## Summary
Completed research on GAMSLIB structure and access methods.

## Deliverables
- docs/research/GAMSLIB_ACCESS_RESEARCH.md
- Sample model downloads verified

## Unknowns Verified
- 1.1: URL structure for GAMSLIB models
- 1.2: gamslib command-line tool capabilities
- 1.3: Metadata available on model pages
- 1.5: Model dependencies ($include files)
- 1.6: GAMSLIB web structure stability

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 2 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 3: Validate GAMS Local Environment

### Prompt

```
On a new branch, complete Prep Task 3 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Validate GAMS Local Environment.

## TASK OBJECTIVES

Verify GAMS installation is correctly configured and can execute models for convexity verification.

## WHAT NEEDS TO BE DONE

1. **Verify GAMS Installation (20 min)**
   ```bash
   # Check GAMS is accessible
   which gams
   gams --version
   
   # Check GAMS directory
   ls -la /Library/Frameworks/GAMS.framework/Versions/51/Resources/
   ```

2. **Test Model Execution (30 min)**
   - Create simple test NLP model
   - Execute with GAMS
   - Verify solver runs and completes
   - Check output file (.lst) generation

3. **Test Solver Options (30 min)**
   - Test with different NLP solvers (CONOPT, IPOPT if available)
   - Verify solver selection works
   - Check solver status codes in output

4. **Test Output Parsing (30 min)**
   - Examine .lst file structure
   - Identify where solve status is reported
   - Identify where objective value is reported
   - Document key parsing patterns

5. **Document Environment Status (10 min)**
   - Update `docs/testing/PATH_SOLVER_STATUS.md` or create new status doc
   - Document GAMS version, solvers available, license status

## DELIVERABLES

- Verified GAMS installation with documented version and configuration
- Test model execution successful
- .lst file parsing patterns documented
- Updated environment status documentation

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 4.3:** Is GAMS installation path consistent across systems?
- **Unknown 4.4:** How to run GAMS non-interactively for batch processing?
- **Unknown 4.5:** How does GAMS handle errors in model files?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add **Findings:** with detailed results
- Add **Evidence:** with specific command outputs or file excerpts
- Add **Decision:** with recommendation based on findings

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 3 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria:
   - [x] GAMS installation verified and accessible
   - [x] Test NLP model executes successfully
   - [x] Solver status correctly captured from output
   - [x] Objective value correctly captured from output
   - [x] .lst file parsing patterns documented
   - [x] Environment documentation updated

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 3: Validate GAMS Local Environment** - Verified GAMS installation, tested model execution and solver options, documented .lst parsing patterns, verified 3 unknowns (4.3, 4.4, 4.5)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 3: Validate GAMS Local Environment

- Verified GAMS installation (version, path, accessibility)
- Tested NLP model execution successfully
- Documented .lst file parsing patterns for status extraction
- Updated environment documentation
- Verified Unknowns 4.3, 4.4, 4.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 3 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 3: Validate GAMS Local Environment" --body "## Summary
Validated GAMS local environment for Sprint 13 convexity verification work.

## Deliverables
- GAMS installation verified
- Test model execution successful
- .lst parsing patterns documented
- Environment documentation updated

## Unknowns Verified
- 4.3: GAMS installation path consistency
- 4.4: Non-interactive batch processing
- 4.5: GAMS error handling

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 3 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 4: Survey GAMSLIB Model Types

### Prompt

```
On a new branch, complete Prep Task 4 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Survey GAMSLIB Model Types.

## TASK OBJECTIVES

Create comprehensive survey of GAMSLIB model types to establish inclusion/exclusion criteria for Sprint 13 model catalog.

## WHAT NEEDS TO BE DONE

1. **Research GAMS Model Type Codes (1 hour)**
   - Document all GAMS model types (LP, NLP, QCP, MIP, etc.)
   - Understand what each type means mathematically
   - Identify which types are convex by definition
   - Reference: GAMS documentation

2. **Analyze GAMSLIB Type Distribution (1 hour)**
   - Browse GAMSLIB web interface by type
   - Count models in each category
   - Identify models that appear in multiple categories
   - Estimate corpus size for NLP + LP

3. **Define Inclusion/Exclusion Criteria (1 hour)**
   - Create clear criteria for inclusion:
     - LP models: Include (convex by definition)
     - NLP models: Include (need convexity verification)
     - QCP models: Include if convex
   - Create clear criteria for exclusion:
     - Integer variables: Exclude (MIP, MILP, MINLP)
     - Complementarity: Exclude (MPEC, MCP)
     - Discontinuous: Exclude (DNLP)
     - General equilibrium: Exclude (MPSGE)
     - System of equations: Exclude (CNS)

4. **Document Findings (30 min)**
   - Create `docs/research/GAMSLIB_MODEL_TYPES.md`
   - Include type definitions
   - Include inclusion/exclusion criteria
   - Include estimated corpus size

## DELIVERABLES

- `docs/research/GAMSLIB_MODEL_TYPES.md` with:
  - Complete list of GAMS model types with definitions
  - Inclusion criteria for Sprint 13 corpus
  - Exclusion criteria with rationale
  - Estimated model counts per type
  - Expected corpus size (target: 50+ models)

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 1.4:** How many NLP and LP models exist in GAMSLIB?
- **Unknown 2.1:** How are GAMS model types declared in model files?
- **Unknown 2.2:** Can we reliably distinguish convex NLP from non-convex NLP by type declaration?
- **Unknown 2.3:** What model types should definitely be excluded?
- **Unknown 2.4:** How should QCP (Quadratically Constrained Programs) be handled?
- **Unknown 2.5:** How do models with RMINLP (Relaxed MINLP) type work?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add **Findings:** with detailed results
- Add **Evidence:** with specific counts, examples, or documentation references
- Add **Decision:** with recommendation based on findings

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 4 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings (model counts, corpus size estimate)
4. Check off all acceptance criteria:
   - [x] All GAMS model types documented with definitions
   - [x] Inclusion criteria clearly specified
   - [x] Exclusion criteria clearly specified with rationale
   - [x] Model counts per type estimated
   - [x] Expected corpus size meets 50+ target
   - [x] Document ready for Sprint 13 reference

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 4: Survey GAMSLIB Model Types** - Created comprehensive model type survey, documented inclusion/exclusion criteria, estimated corpus size, verified 6 unknowns (1.4, 2.1, 2.2, 2.3, 2.4, 2.5)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 4: Survey GAMSLIB Model Types

- Created docs/research/GAMSLIB_MODEL_TYPES.md with:
  - Complete GAMS model type definitions
  - Inclusion criteria (LP, NLP, QCP)
  - Exclusion criteria (MIP, MINLP, MPEC, CNS, DNLP, MPSGE)
  - Model count estimates per type
  - Corpus size estimate (X NLP + Y LP = Z total)
- Verified Unknowns 1.4, 2.1, 2.2, 2.3, 2.4, 2.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 4 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 4: Survey GAMSLIB Model Types" --body "## Summary
Completed comprehensive survey of GAMSLIB model types with inclusion/exclusion criteria.

## Deliverables
- docs/research/GAMSLIB_MODEL_TYPES.md

## Key Findings
- [X] NLP models available
- [Y] LP models available
- [Z] total candidate models (target: 50+)

## Unknowns Verified
- 1.4: NLP and LP model counts
- 2.1: Model type declarations
- 2.2: Convex vs non-convex NLP distinction
- 2.3: Exclusion criteria
- 2.4: QCP handling
- 2.5: RMINLP handling

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 4 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 5: Research Convexity Verification Approaches

### Prompt

```
On a new branch, complete Prep Task 5 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Research Convexity Verification Approaches.

## TASK OBJECTIVES

Research and document approaches for verifying model convexity using GAMS solver output.

## WHAT NEEDS TO BE DONE

1. **Review Existing Convexity Research (30 min)**
   - Read `docs/research/convexity_detection.md`
   - Understand current heuristic approach
   - Identify gaps for solver-based verification

2. **Research GAMS Solver Status Codes (1 hour)**
   - Document GAMS MODEL STATUS codes:
     - 1: Optimal
     - 2: Locally Optimal
     - 3: Unbounded
     - 4: Infeasible
     - 5: Locally Infeasible
     - etc.
   - Document GAMS SOLVER STATUS codes
   - Identify which combinations indicate convexity

3. **Research Solver Selection (1 hour)**
   - Compare NLP solvers available:
     - CONOPT: Interior point, local solver
     - IPOPT: Interior point, local solver
     - BARON: Global solver (if available)
     - ANTIGONE: Global solver (if available)
   - Determine which solver best indicates convexity
   - Document solver availability under demo license

4. **Design Verification Algorithm (1 hour)**
   - Define decision tree for convexity classification:
     ```
     LP model → verified_convex (by definition)
     NLP model + MODEL STATUS = 1 (Optimal) → verified_convex
     NLP model + MODEL STATUS = 2 (Locally Optimal) → locally_optimal (exclude)
     NLP model + MODEL STATUS = 4 (Infeasible) → infeasible (exclude)
     NLP model + MODEL STATUS = 3 (Unbounded) → unbounded (exclude)
     NLP model + error/timeout → unknown (flag for review)
     ```
   - Consider multi-solver validation (optional enhancement)
   - Document edge cases and handling

5. **Document Findings (30 min)**
   - Create `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`
   - Include status code reference
   - Include verification algorithm
   - Include solver recommendations

## DELIVERABLES

- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` with:
  - GAMS MODEL STATUS and SOLVER STATUS code reference
  - Convexity classification algorithm
  - Solver selection recommendations
  - Edge case handling documentation
  - Multi-solver validation approach (optional)

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 3.1:** What GAMS solver status codes indicate global vs local optimality?
- **Unknown 3.2:** Which NLP solver should be used for convexity verification?
- **Unknown 3.3:** How long should convexity verification timeout be?
- **Unknown 3.4:** How to parse objective value and solution status from GAMS .lst file?
- **Unknown 3.5:** How do non-convex models behave with local NLP solvers?
- **Unknown 3.6:** Should we verify convexity with multiple starting points?
- **Unknown 3.7:** How to handle models that are infeasible or unbounded?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add **Findings:** with detailed results
- Add **Evidence:** with specific status codes, test results, or documentation
- Add **Decision:** with recommendation based on findings

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 5 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key algorithm decisions
4. Check off all acceptance criteria:
   - [x] GAMS status codes fully documented
   - [x] Classification algorithm defined and documented
   - [x] Solver recommendations provided
   - [x] Edge cases identified and handling documented
   - [x] Algorithm validated against known convex/non-convex examples
   - [x] Document ready for Sprint 13 implementation

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 5: Research Convexity Verification Approaches** - Designed convexity verification algorithm, documented GAMS status codes, recommended solver selection, verified 7 unknowns (3.1-3.7)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 5: Research Convexity Verification Approaches

- Created docs/research/CONVEXITY_VERIFICATION_DESIGN.md with:
  - GAMS MODEL STATUS and SOLVER STATUS code reference
  - Convexity classification decision tree
  - Solver selection recommendations
  - Edge case handling (infeasible, unbounded, timeout)
- Verified Unknowns 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 5 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 5: Research Convexity Verification Approaches" --body "## Summary
Designed convexity verification approach using GAMS solver status codes.

## Deliverables
- docs/research/CONVEXITY_VERIFICATION_DESIGN.md

## Key Decisions
- Classification algorithm: [brief description]
- Recommended solver: [solver name]
- Timeout: [value] seconds

## Unknowns Verified
- 3.1: Status codes for global vs local optimality
- 3.2: Solver selection
- 3.3: Timeout settings
- 3.4: .lst file parsing
- 3.5: Non-convex model behavior
- 3.6: Multi-start verification
- 3.7: Infeasible/unbounded handling

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 5 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 6: Review Existing nlp2mcp GAMSLIB Work

### Prompt

```
On a new branch, complete Prep Task 6 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Review Existing nlp2mcp GAMSLIB Work.

## TASK OBJECTIVES

Review any existing GAMSLIB-related work in nlp2mcp from EPIC 2 to avoid duplication and build on prior progress.

## WHAT NEEDS TO BE DONE

1. **Inventory Existing GAMSLIB Files (30 min)**
   ```bash
   # Find all GAMSLIB-related files
   find . -name "*gamslib*" -o -name "*GAMSLIB*"
   
   # Find GAMSLIB-related documentation
   find docs -name "*.md" -exec grep -l -i "gamslib" {} \;
   ```

2. **Review EPIC 2 GAMSLIB Research (45 min)**
   - Read `docs/research/gamslib_parse_errors.md`
   - Read `docs/research/gamslib_kpi_definitions.md`
   - Read `docs/research/ingestion_schedule.md`
   - Note: Models tested, features needed, lessons learned

3. **Review Existing Scripts (30 min)**
   - Check for existing download/ingestion scripts
   - Check for existing test fixtures from GAMSLIB
   - Document what exists and what can be reused

4. **Document Findings (15 min)**
   - Create summary of existing work
   - Identify what can be reused for Sprint 13
   - Identify gaps that need new development

## DELIVERABLES

- Inventory of existing GAMSLIB-related code and documentation
- Summary of EPIC 2 GAMSLIB work and lessons learned
- List of reusable components for Sprint 13
- Gap analysis: what needs new development

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 5.1:** What GAMSLIB work exists from EPIC 2?
- **Unknown 5.2:** How does nlp2mcp currently parse model type declarations?
- **Unknown 5.3:** Should the JSON catalog use existing nlp2mcp data structures?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` or `❌ **Status:** WRONG`
- Add **Findings:** with detailed inventory and capabilities
- Add **Evidence:** with specific file paths, code snippets, or documentation excerpts
- Add **Decision:** with recommendation for reuse vs new development

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 6 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was reviewed
3. Fill in the **Result** section with reusable components and gaps
4. Check off all acceptance criteria:
   - [x] All existing GAMSLIB files inventoried
   - [x] EPIC 2 GAMSLIB research reviewed and summarized
   - [x] Reusable components identified
   - [x] Gaps requiring new development documented
   - [x] No unnecessary duplication of existing work

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 6: Review Existing nlp2mcp GAMSLIB Work** - Inventoried existing GAMSLIB code and research, identified reusable components and gaps, verified 3 unknowns (5.1, 5.2, 5.3)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 6: Review Existing nlp2mcp GAMSLIB Work

- Inventoried existing GAMSLIB-related files and documentation
- Reviewed EPIC 2 GAMSLIB research (parse errors, KPIs, ingestion)
- Identified reusable components: [list]
- Identified gaps for new development: [list]
- Verified Unknowns 5.1, 5.2, 5.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 6 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 6: Review Existing nlp2mcp GAMSLIB Work" --body "## Summary
Reviewed existing GAMSLIB work from EPIC 2 to identify reusable components and gaps.

## Inventory
- [X] GAMSLIB-related files found
- [Y] research documents reviewed
- [Z] reusable components identified

## Reusable Components
- [list key reusable items]

## Gaps for New Development
- [list items needing new work]

## Unknowns Verified
- 5.1: Existing GAMSLIB work inventory
- 5.2: Parser model type capabilities
- 5.3: JSON catalog data structure decision

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 6 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 7: Design JSON Catalog Schema (Draft)

### Prompt

```
On a new branch, complete Prep Task 7 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Design JSON Catalog Schema (Draft).

## TASK OBJECTIVES

Create draft JSON schema for the model catalog that will store GAMSLIB model metadata and test status.

## WHAT NEEDS TO BE DONE

1. **Review Sprint 14 Schema Requirements (30 min)**
   - Read PROJECT_PLAN.md Sprint 14 schema specification
   - Understand full tracking requirements
   - Identify minimum fields needed for Sprint 13

2. **Design Sprint 13 Catalog Schema (1 hour)**
   - Minimal schema for initial catalog:
     ```json
     {
       "schema_version": "0.1.0",
       "models": [
         {
           "model_id": "trnsport",
           "model_name": "A Transportation Problem",
           "gamslib_type": "LP",
           "source_url": "https://...",
           "description": "...",
           "author": "...",
           "download_status": "pending|downloaded|failed",
           "download_date": null,
           "file_path": null,
           "file_size_bytes": null,
           "notes": ""
         }
       ]
     }
     ```
   - Extensible for Sprint 14 additions

3. **Create Schema Documentation (30 min)**
   - Document each field
   - Document valid values for status fields
   - Document extension points for Sprint 14

4. **Create Example Catalog (30 min)**
   - Create `data/gamslib/catalog_example.json`
   - Include 3-5 example entries
   - Validate JSON syntax

## DELIVERABLES

- Draft JSON schema documented
- `data/gamslib/catalog_example.json` with sample entries
- Schema documentation with field descriptions
- Extension points for Sprint 14 documented

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 5.3:** Should the JSON catalog use existing nlp2mcp data structures?

For this unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED`
- Add **Findings:** with design decision rationale
- Add **Evidence:** with schema design details
- Add **Decision:** with final recommendation (standalone vs integrated)

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 7 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with what was created
3. Fill in the **Result** section with schema summary
4. Check off all acceptance criteria:
   - [x] Minimal schema for Sprint 13 defined
   - [x] Schema documented with field descriptions
   - [x] Example catalog created with valid JSON
   - [x] Extension points for Sprint 14 identified
   - [x] Schema supports 50+ model entries

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 7: Design JSON Catalog Schema (Draft)** - Created draft catalog schema for GAMSLIB models, documented field descriptions and extension points, created example catalog
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 7: Design JSON Catalog Schema (Draft)

- Created draft JSON schema for GAMSLIB model catalog
- Documented all fields with descriptions and valid values
- Created data/gamslib/catalog_example.json with sample entries
- Documented extension points for Sprint 14 schema expansion
- Updated PREP_PLAN.md Task 7 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 7: Design JSON Catalog Schema (Draft)" --body "## Summary
Created draft JSON schema for GAMSLIB model catalog.

## Deliverables
- data/gamslib/catalog_example.json
- Schema documentation

## Schema Fields
- model_id, model_name, gamslib_type
- source_url, description, author
- download_status, download_date
- file_path, file_size_bytes, notes

## Extension Points for Sprint 14
- convexity status fields
- parse/translate/solve status fields
- timing and version tracking

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 7 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 8: Create Test Model Set

### Prompt

```
On a new branch, complete Prep Task 8 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Create Test Model Set.

## TASK OBJECTIVES

Download a small set of known-good test models to use for validating Sprint 13 infrastructure.

## WHAT NEEDS TO BE DONE

1. **Select Test Models (30 min)**
   - Select 5 LP models (known convex)
   - Select 5 NLP models (mix of convex and non-convex)
   - Select 2-3 models of excluded types (MIP, MPEC) for testing exclusion
   - Document selection rationale

2. **Download Test Models (30 min)**
   - Use method determined in Task 2 (gamslib command or web)
   - Save to `tests/fixtures/gamslib_test_models/`
   - Verify each download successful

3. **Validate Test Models (30 min)**
   - Run each model with GAMS
   - Verify they solve without errors
   - Document expected convexity status for each

4. **Create Test Model Manifest (30 min)**
   - Create `tests/fixtures/gamslib_test_models/MANIFEST.md`
   - List each model with: name, type, expected convexity, notes
   - Include verification commands

## DELIVERABLES

- `tests/fixtures/gamslib_test_models/` directory with 12-15 test models
- `tests/fixtures/gamslib_test_models/MANIFEST.md` with model documentation
- Each model verified to execute successfully
- Expected convexity status documented for each model

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 1.5:** Are there dependencies between GAMSLIB models ($include files)?
- **Unknown 2.1:** How are GAMS model types declared in model files?
- **Unknown 3.5:** How do non-convex models behave with local NLP solvers?

For each unknown, update with additional evidence from testing if not already verified.

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 8 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with models downloaded and manifest created
3. Fill in the **Result** section with test model summary
4. Check off all acceptance criteria:
   - [x] 5 LP test models downloaded
   - [x] 5 NLP test models downloaded
   - [x] 2-3 excluded type models downloaded
   - [x] All models execute successfully with GAMS
   - [x] Expected convexity status documented
   - [x] Manifest file complete

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 8: Create Test Model Set** - Downloaded 12-15 test models from GAMSLIB, created manifest with expected convexity status, verified all models execute successfully
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 8: Create Test Model Set

- Downloaded test models to tests/fixtures/gamslib_test_models/:
  - 5 LP models (known convex)
  - 5 NLP models (mix of convex/non-convex)
  - 2-3 excluded type models (MIP, MPEC)
- Created MANIFEST.md with model documentation
- Verified all models execute successfully with GAMS
- Documented expected convexity status for each model
- Updated PREP_PLAN.md Task 8 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 8: Create Test Model Set" --body "## Summary
Created test model set for validating Sprint 13 infrastructure.

## Test Models
### LP Models (5)
- [list models]

### NLP Models (5)
- [list models]

### Excluded Type Models (2-3)
- [list models]

## Deliverables
- tests/fixtures/gamslib_test_models/ with 12-15 models
- tests/fixtures/gamslib_test_models/MANIFEST.md

## Verification
All models execute successfully with GAMS.

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 8 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 9: Audit GAMS License Capabilities

### Prompt

```
On a new branch, complete Prep Task 9 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Audit GAMS License Capabilities.

## TASK OBJECTIVES

Document GAMS license capabilities and limitations that may affect Sprint 13 work.

## WHAT NEEDS TO BE DONE

1. **Check Current License (20 min)**
   ```bash
   gams license
   ```
   - Document license type
   - Document expiration date (if any)
   - Note any restrictions displayed

2. **Test Size Limits (40 min)**
   - Create models of increasing size (100, 500, 1000, 5000 variables)
   - Execute each and note any license limit errors
   - Document maximum model size under current license

3. **Check Solver Availability (30 min)**
   ```bash
   gams solvers
   ```
   - List all available solvers
   - Note which NLP solvers are available
   - Note which global solvers are available (if any)

4. **Document Findings (30 min)**
   - Update or create license status documentation
   - Document size limits
   - Document solver availability
   - Note any GAMSLIB models that may exceed limits

## DELIVERABLES

- Documented license type and capabilities
- Model size limits tested and documented
- Available solver list documented
- Recommendations for handling license limitations

## KNOWN UNKNOWNS TO VERIFY

Update the following unknowns in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`:

- **Unknown 4.1:** What solvers are available under GAMS demo license?
- **Unknown 4.2:** What are the model size limits under demo license?

For each unknown, update the "Verification Results" section with:
- Change status from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED`
- Add **Findings:** with specific solver list and size limits
- Add **Evidence:** with command outputs and test results
- Add **Decision:** with recommendations for handling limitations

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 9 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with documentation created/updated
3. Fill in the **Result** section with license summary
4. Check off all acceptance criteria:
   - [x] License type documented
   - [x] Model size limits tested and documented
   - [x] Available solvers listed
   - [x] Limitations that may affect Sprint 13 identified
   - [x] Workarounds or recommendations provided

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 9: Audit GAMS License Capabilities** - Documented license type and capabilities, tested model size limits, listed available solvers, verified 2 unknowns (4.1, 4.2)
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 9: Audit GAMS License Capabilities

- Documented GAMS license type and capabilities
- Tested model size limits: max [X] variables, [Y] equations
- Listed available solvers: [list NLP solvers]
- Identified limitations affecting Sprint 13
- Provided recommendations for handling license restrictions
- Verified Unknowns 4.1, 4.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 9 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 9: Audit GAMS License Capabilities" --body "## Summary
Audited GAMS license capabilities and limitations.

## License Status
- Type: [license type]
- Expiration: [date or N/A]

## Size Limits
- Max variables: [X]
- Max equations: [Y]
- Max nonzeros: [Z]

## Available Solvers
### NLP Solvers
- [list]

### Global Solvers
- [list or N/A]

## Recommendations
- [handling recommendations]

## Unknowns Verified
- 4.1: Available solvers
- 4.2: Model size limits

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 9 are met."
```

Then wait for reviewer comments before merging.
```

---

## Task 10: Plan Sprint 13 Detailed Schedule

### Prompt

```
On a new branch, complete Prep Task 10 from docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md: Plan Sprint 13 Detailed Schedule.

## TASK OBJECTIVES

Create detailed Sprint 13 plan incorporating findings from all prep tasks.

## WHAT NEEDS TO BE DONE

1. **Review All Prep Task Findings (1 hour)**
   - Incorporate Task 1 Known Unknowns
   - Incorporate Task 2 GAMSLIB access findings
   - Incorporate Task 3 environment validation
   - Incorporate Task 4 model type survey
   - Incorporate Task 5 convexity verification design
   - Incorporate Task 6 existing work review
   - Incorporate Task 7 schema design
   - Incorporate Task 9 license audit

2. **Create Day-by-Day Plan (1.5 hours)**

   **Days 1-2: Model Discovery & Catalog Creation**
   - Day 1: Implement catalog schema, set up directory structure
   - Day 2: Scrape/download model list, populate initial catalog

   **Days 3-4: Download Infrastructure**
   - Day 3: Implement download script
   - Day 4: Test with full model set, handle edge cases

   **Days 5-6: Convexity Verification Foundation**
   - Day 5: Implement GAMS execution framework
   - Day 6: Implement classification logic, initial verification run

   **Days 7-8: Integration & Testing**
   - Day 7: Integration testing, bug fixes
   - Day 8: Documentation, checkpoint review

   **Days 9-10: Buffer & Polish**
   - Day 9: Address issues from testing
   - Day 10: Final documentation, sprint review prep

3. **Define Checkpoints (30 min)**
   - Day 3: Model catalog populated (50+ entries)
   - Day 5: Download script functional
   - Day 7: Convexity verification working
   - Day 10: All acceptance criteria met

4. **Create Sprint 13 Plan Document (1 hour)**
   - Use template from EPIC 1/2
   - Include all sections: Goals, Day-by-Day, Risks, Checkpoints, Acceptance Criteria

## DELIVERABLES

- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` with:
  - Sprint goals (from PROJECT_PLAN.md)
  - Day-by-day detailed plan
  - Risk identification and mitigation
  - Checkpoint schedule (Days 3, 5, 7, 10)
  - Acceptance criteria
  - Known unknowns verification schedule

## KNOWN UNKNOWNS TO VERIFY

This task integrates findings from all other prep tasks. Ensure all 26 unknowns in KNOWN_UNKNOWNS.md have been addressed by previous tasks.

Review the Task-to-Unknown Mapping table in KNOWN_UNKNOWNS.md and confirm:
- All Critical unknowns are verified
- All High unknowns are verified
- Any remaining Medium/Low unknowns have mitigation plans

## UPDATE PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md`:

1. Change Task 10 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the **Changes** section with plan document created
3. Fill in the **Result** section with plan summary
4. Check off all acceptance criteria:
   - [x] Plan incorporates all prep task findings
   - [x] Day-by-day plan covers all sprint components
   - [x] Risks identified with mitigation strategies
   - [x] Checkpoints defined with clear criteria
   - [x] Known unknowns scheduled for verification
   - [x] Plan reviewed and approved

## UPDATE CHANGELOG.md

Add an entry to CHANGELOG.md:

```markdown
- **Task 10: Plan Sprint 13 Detailed Schedule** - Created comprehensive day-by-day Sprint 13 plan, incorporated all prep task findings, defined checkpoints and risk mitigation
```

## QUALITY GATE

Before committing, run quality checks if any Python code was modified:
```bash
make typecheck && make lint && make format && make test
```

## COMMIT MESSAGE FORMAT

```
Complete Sprint 13 Prep Task 10: Plan Sprint 13 Detailed Schedule

- Created docs/planning/EPIC_3/SPRINT_13/PLAN.md with:
  - Sprint goals and success criteria
  - Day-by-day detailed plan (Days 1-10)
  - Risk identification and mitigation strategies
  - Checkpoint schedule (Days 3, 5, 7, 10)
  - Integration of all prep task findings
- Verified all Critical and High unknowns are resolved
- Updated PREP_PLAN.md Task 10 status to COMPLETE
```

## CREATE PULL REQUEST

After pushing, create a PR using gh:
```bash
gh pr create --title "Complete Sprint 13 Prep Task 10: Plan Sprint 13 Detailed Schedule" --body "## Summary
Created comprehensive Sprint 13 plan incorporating all prep task findings.

## Sprint 13 Plan Overview

### Days 1-2: Model Discovery & Catalog Creation
### Days 3-4: Download Infrastructure
### Days 5-6: Convexity Verification Foundation
### Days 7-8: Integration & Testing
### Days 9-10: Buffer & Polish

## Checkpoints
- Day 3: Model catalog populated (50+ entries)
- Day 5: Download script functional
- Day 7: Convexity verification working
- Day 10: All acceptance criteria met

## Prep Task Integration
All 9 prep tasks incorporated into plan.

## Unknown Resolution Status
- Critical: [X]/7 verified
- High: [Y]/10 verified
- Medium: [Z]/6 verified
- Low: [W]/3 verified

## Acceptance Criteria
All criteria from PREP_PLAN.md Task 10 are met."
```

Then wait for reviewer comments before merging.
```

---

## Summary: Task-to-Unknown Mapping Reference

| Prep Task | Unknowns Verified |
|-----------|-------------------|
| Task 2: Research GAMSLIB Structure and Access | 1.1, 1.2, 1.3, 1.5, 1.6 |
| Task 3: Validate GAMS Local Environment | 4.3, 4.4, 4.5 |
| Task 4: Survey GAMSLIB Model Types | 1.4, 2.1, 2.2, 2.3, 2.4, 2.5 |
| Task 5: Research Convexity Verification Approaches | 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7 |
| Task 6: Review Existing nlp2mcp GAMSLIB Work | 5.1, 5.2, 5.3 |
| Task 7: Design JSON Catalog Schema (Draft) | 5.3 (contributes) |
| Task 8: Create Test Model Set | 1.5, 2.1, 3.5 (contributes/validates) |
| Task 9: Audit GAMS License Capabilities | 4.1, 4.2 |
| Task 10: Plan Sprint 13 Detailed Schedule | All (integrates) |
