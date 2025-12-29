# Sprint 13 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 13 GAMSLIB infrastructure work begins  
**Timeline:** Complete before Sprint 13 Day 1  
**Goal:** Research GAMSLIB structure, validate GAMS environment, and establish foundation for model discovery and convexity verification

**Key Context from EPIC 3:** Sprint 13 initiates a new epic focused on building local testing infrastructure using GAMSLIB as a validation corpus. This requires understanding GAMSLIB organization, GAMS licensing/environment, and convexity verification approaches before implementation.

---

## Executive Summary

Sprint 13 is the first sprint of EPIC 3, which focuses on GAMSLIB validation and comprehensive testing infrastructure. The sprint goals include:
1. **Model Discovery** - Identify and catalog 50+ NLP/LP models from GAMSLIB
2. **Download Infrastructure** - Create scripts to download models from GAMS Model Library
3. **Convexity Verification Foundation** - Build system to verify models are truly convex

This prep plan addresses research and validation tasks that must be completed before implementation to prevent blocking issues during the sprint.

**Key Insight from EPIC 2:** Known Unknowns process achieved excellent results - proactive identification prevents late surprises. Continue this practice for EPIC 3.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 13 Known Unknowns List | Critical | 2-3 hours | None | All Sprint 13 goals |
| 2 | Research GAMSLIB Structure and Access | Critical | 3-4 hours | Task 1 | Model Discovery |
| 3 | Validate GAMS Local Environment | Critical | 2 hours | None | Convexity Verification |
| 4 | Survey GAMSLIB Model Types | High | 3-4 hours | Task 2 | Model Discovery |
| 5 | Research Convexity Verification Approaches | High | 3-4 hours | Task 1, Task 3 | Convexity Verification |
| 6 | Review Existing nlp2mcp GAMSLIB Work | High | 2 hours | None | All goals |
| 7 | Design JSON Catalog Schema (Draft) | Medium | 2-3 hours | Task 4 | Model Discovery |
| 8 | Create Test Model Set | Medium | 2 hours | Task 2, Task 3 | Download Infrastructure |
| 9 | Audit GAMS License Capabilities | Medium | 1-2 hours | Task 3 | Convexity Verification |
| 10 | Plan Sprint 13 Detailed Schedule | Critical | 3-4 hours | All tasks | Sprint planning |

**Total Estimated Time:** ~24-30 hours (~3-4 working days)

**Critical Path:** Tasks 1 → 2 → 4 → 7 → 10 (must complete before Sprint 13)

---

## Task 1: Create Sprint 13 Known Unknowns List

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Sprint planning  
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 13 to prevent late-sprint discoveries that derail progress.

### Why This Matters

EPIC 2 demonstrated the value of Known Unknowns documentation. Sprint 13 introduces new territory (GAMSLIB integration, convexity verification) with many potential assumptions that need validation.

### Background

From EPIC 2 Known Unknowns process:
- 22+ unknowns identified per sprint
- Critical unknowns verified before implementation
- Zero late surprises when process followed
- Template and process already established in `docs/planning/KNOWN_UNKNOWNS_PROMPT_TEMPLATE.md`

### What Needs to Be Done

1. **Review Sprint 13 scope from PROJECT_PLAN.md**
   - Model Discovery & Classification (~12-15h)
   - Download Script Development (~4-5h)
   - Convexity Verification Foundation (~8-10h)
   - Directory Structure Setup (~2h)

2. **Identify unknowns in each category:**

   **Category 1: GAMSLIB Access and Structure**
   - How is GAMSLIB organized (directories, naming conventions)?
   - Is authentication required to download models?
   - What metadata is available for each model?
   - Are there rate limits or access restrictions?
   - What's the URL structure for model downloads?

   **Category 2: Model Type Classification**
   - How are model types declared in GAMSLIB (NLP, LP, MIP, etc.)?
   - Are model type declarations reliable/accurate?
   - Do some models have multiple valid type classifications?
   - How to handle models with ambiguous types?

   **Category 3: Convexity Verification**
   - Which GAMS solver to use for convexity verification?
   - How to distinguish global vs local optima in solver output?
   - What timeout is appropriate for verification?
   - How to handle models that require specific solver options?
   - Can all NLP models be solved with default settings?

   **Category 4: GAMS Environment**
   - Is current GAMS installation sufficient for all models?
   - What solvers are available under current license?
   - Are there model size limits under demo license?
   - How to handle models requiring commercial solver features?

   **Category 5: Integration with Existing Code**
   - Does nlp2mcp have existing GAMSLIB-related code to build on?
   - Are there existing test fixtures from GAMSLIB?
   - How does this work relate to EPIC 2 GAMSLib work?

3. **For each unknown, document:**
   - Assumption (what we currently believe)
   - How to verify (specific test or research)
   - Priority (Critical/High/Medium/Low)
   - Risk if wrong (impact on sprint)
   - Verification deadline (Day 0, Day 1, etc.)

4. **Create document with all categories**

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify document exists and has required structure
test -f docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md && echo "Document exists"

# Check for required categories
grep -c "Category" docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md
# Expected: 5+ categories

# Check for unknown count
grep -c "Unknown" docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md
# Expected: 20+ unknowns
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` with 20+ unknowns across 5 categories
- All Critical/High unknowns have verification plans
- Verification deadlines assigned

### Acceptance Criteria

- [ ] Document created with 20+ unknowns across 5 categories
- [ ] All unknowns have assumption, verification method, priority
- [ ] All Critical/High unknowns have verification plan
- [ ] Unknowns cover all Sprint 13 components
- [ ] Template for updates defined
- [ ] Research time estimated

---

## Task 2: Research GAMSLIB Structure and Access

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Research the structure, organization, and access methods for the GAMS Model Library to inform download script development.

### Why This Matters

Sprint 13 requires downloading 50+ models from GAMSLIB. Without understanding the library structure, URL patterns, and access methods, the download script development will be blocked or require significant rework.

### Background

GAMS Model Library (GAMSLIB) is the official collection of example models distributed with GAMS. Key reference:
- URL: https://www.gams.com/latest/gamslib_ml/libhtml/
- Contains hundreds of models across many optimization types
- Models are documented with metadata (author, type, description)

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Test gamslib command availability
gamslib --help 2>/dev/null || echo "gamslib command not available"

# Test model extraction (if available)
gamslib trnsport /tmp/trnsport.gms 2>/dev/null && echo "Model extracted"

# Verify research document exists
test -f docs/research/GAMSLIB_ACCESS_RESEARCH.md && echo "Research document exists"
```

### Deliverables

- `docs/research/GAMSLIB_ACCESS_RESEARCH.md` with:
  - GAMSLIB URL structure documentation
  - Model page metadata analysis
  - Access method comparison (web vs command-line)
  - Recommended approach for download script
- Test downloads of 3-5 sample models

### Acceptance Criteria

- [ ] GAMSLIB web structure documented
- [ ] URL patterns for models identified
- [ ] Authentication requirements determined
- [ ] gamslib command-line tool evaluated
- [ ] Recommended download approach documented
- [ ] Sample models successfully downloaded

---

## Task 3: Validate GAMS Local Environment

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Verify GAMS installation is correctly configured and can execute models for convexity verification.

### Why This Matters

Sprint 13 Convexity Verification Foundation requires executing GAMS models locally and capturing solver output. Any environment issues discovered during the sprint will block progress.

### Background

From EPIC 2 PATH Solver work:
- GAMS Version: 51.3.0 installed at `/Library/Frameworks/GAMS.framework/Versions/51/Resources/`
- PATH Solver: Version 5.2.01 (included with GAMS)
- License: Demo license
- Reference: `docs/testing/PATH_SOLVER_STATUS.md`

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify GAMS accessible
gams --version

# Run test model
echo '
Variables x, y, obj;
x.lo = 0; x.up = 10;
y.lo = 0; y.up = 10;
Equations objdef, constraint;
objdef.. obj =e= x*x + y*y;
constraint.. x + y =g= 1;
Model test /all/;
Solve test using NLP minimizing obj;
Display x.l, y.l, obj.l;
' > /tmp/test_nlp.gms

gams /tmp/test_nlp.gms

# Check for successful solve
grep "SOLVER STATUS" /tmp/test_nlp.lst
grep "MODEL STATUS" /tmp/test_nlp.lst
```

### Deliverables

- Verified GAMS installation with documented version and configuration
- Test model execution successful
- .lst file parsing patterns documented
- Updated environment status documentation

### Acceptance Criteria

- [ ] GAMS installation verified and accessible
- [ ] Test NLP model executes successfully
- [ ] Solver status correctly captured from output
- [ ] Objective value correctly captured from output
- [ ] .lst file parsing patterns documented
- [ ] Environment documentation updated

---

## Task 4: Survey GAMSLIB Model Types

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (GAMSLIB Structure Research)

### Objective

Create comprehensive survey of GAMSLIB model types to establish inclusion/exclusion criteria for Sprint 13 model catalog.

### Why This Matters

Sprint 13 must identify 50+ NLP and LP models suitable for MCP reformulation. This requires understanding:
- What model types exist in GAMSLIB
- Which types are suitable (NLP, LP, QCP)
- Which types must be excluded (MIP, MINLP, MPEC, etc.)
- How types are declared/identified

### Background

From PROJECT_PLAN.md Sprint 13 Components:
- Target: NLP (nonlinear programs) and LP (linear programs)
- Exclude: MIP, MILP, MINLP, MPEC, MPSGE, CNS, DNLP
- Deliverable: `docs/research/GAMSLIB_MODEL_TYPES.md`

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify research document exists
test -f docs/research/GAMSLIB_MODEL_TYPES.md && echo "Document exists"

# Check for required sections
grep -c "## " docs/research/GAMSLIB_MODEL_TYPES.md
# Expected: 4+ sections (Types, Inclusion, Exclusion, Estimates)
```

### Deliverables

- `docs/research/GAMSLIB_MODEL_TYPES.md` with:
  - Complete list of GAMS model types with definitions
  - Inclusion criteria for Sprint 13 corpus
  - Exclusion criteria with rationale
  - Estimated model counts per type
  - Expected corpus size (target: 50+ models)

### Acceptance Criteria

- [ ] All GAMS model types documented with definitions
- [ ] Inclusion criteria clearly specified
- [ ] Exclusion criteria clearly specified with rationale
- [ ] Model counts per type estimated
- [ ] Expected corpus size meets 50+ target
- [ ] Document ready for Sprint 13 reference

---

## Task 5: Research Convexity Verification Approaches

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns), Task 3 (GAMS Environment)

### Objective

Research and document approaches for verifying model convexity using GAMS solver output.

### Why This Matters

Sprint 13 requires classifying models as convex or non-convex. The approach must be:
- Reliable (correctly identify convex models)
- Practical (work with available solvers)
- Automatable (scriptable for batch processing)

### Background

From `docs/research/convexity_detection.md` (EPIC 2):
- Heuristic convexity detection implemented for warnings
- AST-based convexity classification explored
- Solver-based verification not yet implemented

From PROJECT_PLAN.md Sprint 13:
- Analyze solver termination status for classification
- LP models automatically classified as convex
- NLP models require solver verification

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify research document exists
test -f docs/research/CONVEXITY_VERIFICATION_DESIGN.md && echo "Document exists"

# Check for algorithm documentation
grep "verified_convex" docs/research/CONVEXITY_VERIFICATION_DESIGN.md
```

### Deliverables

- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` with:
  - GAMS MODEL STATUS and SOLVER STATUS code reference
  - Convexity classification algorithm
  - Solver selection recommendations
  - Edge case handling documentation
  - Multi-solver validation approach (optional)

### Acceptance Criteria

- [ ] GAMS status codes fully documented
- [ ] Classification algorithm defined and documented
- [ ] Solver recommendations provided
- [ ] Edge cases identified and handling documented
- [ ] Algorithm validated against known convex/non-convex examples
- [ ] Document ready for Sprint 13 implementation

---

## Task 6: Review Existing nlp2mcp GAMSLIB Work

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Review any existing GAMSLIB-related work in nlp2mcp from EPIC 2 to avoid duplication and build on prior progress.

### Why This Matters

EPIC 2 included GAMSLib integration work (Sprints 7-8, 11-12). Sprint 13 should build on this foundation rather than starting from scratch.

### Background

From EPIC 2 PROJECT_PLAN.md:
- Sprint 7-8: GAMSLib Integration Part 1 & 2
- Sprint 11-12: Tier 1 and Tier 2 GAMSLIB models
- Existing research: `docs/research/gamslib_*.md`

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# List GAMSLIB-related files
find . -name "*gamslib*" -type f 2>/dev/null | head -20

# Check for existing test fixtures
ls -la tests/fixtures/gamslib/ 2>/dev/null || echo "No GAMSLIB fixtures directory"
```

### Deliverables

- Inventory of existing GAMSLIB-related code and documentation
- Summary of EPIC 2 GAMSLIB work and lessons learned
- List of reusable components for Sprint 13
- Gap analysis: what needs new development

### Acceptance Criteria

- [ ] All existing GAMSLIB files inventoried
- [ ] EPIC 2 GAMSLIB research reviewed and summarized
- [ ] Reusable components identified
- [ ] Gaps requiring new development documented
- [ ] No unnecessary duplication of existing work

---

## Task 7: Design JSON Catalog Schema (Draft)

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** Task 4 (Model Types Survey)

### Objective

Create draft JSON schema for the model catalog that will store GAMSLIB model metadata and test status.

### Why This Matters

Sprint 14 will formalize the JSON database schema, but Sprint 13 needs an initial catalog structure for storing discovered models. Having a draft schema ready enables faster Sprint 13 implementation.

### Background

From PROJECT_PLAN.md Sprint 14:
- Comprehensive JSON schema for model tracking
- Fields: model_id, model_name, gamslib_type, convexity status, parse/translate/solve status
- Schema validation planned for Sprint 14

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify example catalog is valid JSON
python -c "import json; json.load(open('data/gamslib/catalog_example.json'))" && echo "Valid JSON"

# Check for required fields
python -c "
import json
catalog = json.load(open('data/gamslib/catalog_example.json'))
model = catalog['models'][0]
required = ['model_id', 'model_name', 'gamslib_type', 'download_status']
for field in required:
    assert field in model, f'Missing field: {field}'
print('All required fields present')
"
```

### Deliverables

- Draft JSON schema documented
- `data/gamslib/catalog_example.json` with sample entries
- Schema documentation with field descriptions
- Extension points for Sprint 14 documented

### Acceptance Criteria

- [ ] Minimal schema for Sprint 13 defined
- [ ] Schema documented with field descriptions
- [ ] Example catalog created with valid JSON
- [ ] Extension points for Sprint 14 identified
- [ ] Schema supports 50+ model entries

---

## Task 8: Create Test Model Set

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 13 Day 3  
**Owner:** Development team  
**Dependencies:** Task 2 (GAMSLIB Access), Task 3 (GAMS Environment)

### Objective

Download a small set of known-good test models to use for validating Sprint 13 infrastructure.

### Why This Matters

Sprint 13 will build download scripts and convexity verification. Having a known-good test set enables:
- Testing download script with real models
- Testing convexity verification with known convex/non-convex examples
- Rapid iteration without waiting for full corpus

### Background

From EPIC 2:
- Tier 1 models already tested with nlp2mcp
- Models like trnsport, simple LP problems known to work
- Reference: `docs/status/GAMSLIB_CONVERSION_STATUS.md` (if exists)

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify test models exist
ls tests/fixtures/gamslib_test_models/*.gms | wc -l
# Expected: 12-15 models

# Verify manifest exists
test -f tests/fixtures/gamslib_test_models/MANIFEST.md && echo "Manifest exists"

# Test one model executes
gams tests/fixtures/gamslib_test_models/trnsport.gms 2>/dev/null && echo "Model executes"
```

### Deliverables

- `tests/fixtures/gamslib_test_models/` directory with 12-15 test models
- `tests/fixtures/gamslib_test_models/MANIFEST.md` with model documentation
- Each model verified to execute successfully
- Expected convexity status documented for each model

### Acceptance Criteria

- [ ] 5 LP test models downloaded
- [ ] 5 NLP test models downloaded
- [ ] 2-3 excluded type models downloaded
- [ ] All models execute successfully with GAMS
- [ ] Expected convexity status documented
- [ ] Manifest file complete

---

## Task 9: Audit GAMS License Capabilities

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (GAMS Environment)

### Objective

Document GAMS license capabilities and limitations that may affect Sprint 13 work.

### Why This Matters

GAMS demo license has limitations (model size, solver access). Understanding these upfront prevents surprises when processing larger GAMSLIB models.

### Background

From EPIC 2 PATH Solver work:
- Demo license sufficient for small/medium test problems
- Limits documented in `docs/testing/PATH_SOLVER_STATUS.md`

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Check license status
gams license 2>&1 | head -20

# List available solvers
gams solvers 2>&1 | grep -i nlp
```

### Deliverables

- Documented license type and capabilities
- Model size limits tested and documented
- Available solver list documented
- Recommendations for handling license limitations

### Acceptance Criteria

- [ ] License type documented
- [ ] Model size limits tested and documented
- [ ] Available solvers listed
- [ ] Limitations that may affect Sprint 13 identified
- [ ] Workarounds or recommendations provided

---

## Task 10: Plan Sprint 13 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 13 Day 1  
**Owner:** Sprint planning  
**Dependencies:** All tasks

### Objective

Create detailed Sprint 13 plan incorporating findings from all prep tasks.

### Why This Matters

Sprint 13 is the first sprint of a new epic. A well-structured plan ensures:
- Clear daily objectives
- Identified risks addressed
- Known unknowns scheduled for verification
- Checkpoints defined for progress monitoring

### Background

From PROJECT_PLAN.md Sprint 13:
- Estimated Effort: 22-27 hours
- Components: Model Discovery (~12-15h), Convexity Verification (~8-10h), Directory Setup (~2h)
- Deliverables: 50+ models cataloged, download script, verification script

### What Needs to Be Done

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

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify plan document exists
test -f docs/planning/EPIC_3/SPRINT_13/PLAN.md && echo "Plan exists"

# Check for required sections
grep -c "## Day" docs/planning/EPIC_3/SPRINT_13/PLAN.md
# Expected: 10 (one per day)

grep "Checkpoint" docs/planning/EPIC_3/SPRINT_13/PLAN.md && echo "Checkpoints defined"
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` with:
  - Sprint goals (from PROJECT_PLAN.md)
  - Day-by-day detailed plan
  - Risk identification and mitigation
  - Checkpoint schedule (Days 3, 5, 7, 10)
  - Acceptance criteria
  - Known unknowns verification schedule

### Acceptance Criteria

- [ ] Plan incorporates all prep task findings
- [ ] Day-by-day plan covers all sprint components
- [ ] Risks identified with mitigation strategies
- [ ] Checkpoints defined with clear criteria
- [ ] Known unknowns scheduled for verification
- [ ] Plan reviewed and approved

---

## Summary

### Critical Path

```
Task 1 (Known Unknowns)
    ↓
Task 2 (GAMSLIB Structure) ←── Task 3 (GAMS Environment)
    ↓                              ↓
Task 4 (Model Types)          Task 5 (Convexity Verification)
    ↓                              ↓
Task 7 (Schema Design)        Task 9 (License Audit)
    ↓                              ↓
    └──────────────────────────────┘
                  ↓
        Task 10 (Sprint Plan)
```

Tasks 6 and 8 can proceed in parallel after their dependencies.

### Success Criteria

- [ ] All 10 prep tasks completed
- [ ] Sprint 13 Known Unknowns documented (20+ unknowns)
- [ ] GAMSLIB access method validated
- [ ] GAMS environment verified working
- [ ] Model type inclusion/exclusion criteria defined
- [ ] Convexity verification approach designed
- [ ] Existing work reviewed, reusable components identified
- [ ] JSON catalog schema drafted
- [ ] Test model set created and validated
- [ ] License capabilities documented
- [ ] Sprint 13 detailed plan created

### Estimated Total Time

| Task | Estimated Time |
|------|----------------|
| Task 1: Known Unknowns | 2-3 hours |
| Task 2: GAMSLIB Structure | 3-4 hours |
| Task 3: GAMS Environment | 2 hours |
| Task 4: Model Types Survey | 3-4 hours |
| Task 5: Convexity Verification | 3-4 hours |
| Task 6: Existing Work Review | 2 hours |
| Task 7: Schema Design | 2-3 hours |
| Task 8: Test Model Set | 2 hours |
| Task 9: License Audit | 1-2 hours |
| Task 10: Sprint Plan | 3-4 hours |
| **Total** | **24-30 hours** |

---

## Appendix: Document Cross-References

### Sprint Goals Reference
- `docs/planning/EPIC_3/PROJECT_PLAN.md` - Sprint 13 section (lines 7-89)
- `docs/planning/EPIC_3/GOALS.md` - EPIC 3 objectives

### Research Documents
- `docs/research/convexity_detection.md` - EPIC 2 convexity detection work
- `docs/research/gamslib_parse_errors.md` - EPIC 2 GAMSLIB parse analysis
- `docs/research/gamslib_kpi_definitions.md` - EPIC 2 KPI definitions
- `docs/research/ingestion_schedule.md` - EPIC 2 ingestion schedule

### Process Templates
- `docs/planning/KNOWN_UNKNOWNS_PROMPT_TEMPLATE.md` - Known unknowns template
- `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md` - PREP_PLAN example
- `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md` - PREP_PLAN example

### Environment Documentation
- `docs/testing/PATH_SOLVER_STATUS.md` - GAMS/PATH environment status

---

## Changelog

- **2025-12-29:** Initial Sprint 13 PREP_PLAN created
