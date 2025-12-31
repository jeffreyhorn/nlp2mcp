# Sprint 13 Known Unknowns

**Created:** December 29, 2025  
**Status:** Active - Pre-Sprint 13  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 13 GAMSLIB discovery, download infrastructure, and convexity verification foundation

---

## Overview

This document identifies all assumptions and unknowns for Sprint 13 features **before** implementation begins. This proactive approach continues the highly successful methodology from EPIC 1 and EPIC 2 that prevented late-stage surprises.

**Sprint 13 Scope:**
1. GAMSLIB Model Discovery & Classification (~12-15h) - Research structure, catalog models
2. Download Script Development (~4-5h) - Automate model downloads
3. Convexity Verification Foundation (~8-10h) - GAMS execution, classification logic
4. Directory Structure Setup (~2h) - Data organization and gitignore

**Reference:** See `docs/planning/EPIC_3/PROJECT_PLAN.md` lines 7-89 for complete Sprint 13 deliverables and acceptance criteria.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule  
- Sprint 6-12: Consistent success, enabled realistic scope setting

**EPIC 3 Context:** Sprint 13 initiates a new epic focused on GAMSLIB validation. This is infrastructure work that must be solid before Sprints 14-17 can build upon it. Unknown verification is critical to avoid downstream issues.

---

## How to Use This Document

### Before Sprint 13 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 13
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 26  
**By Priority:**
- Critical: 7 (unknowns that could derail sprint or prevent 50+ model catalog)
- High: 10 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (GAMSLIB Access & Structure): 6 unknowns
- Category 2 (Model Type Classification): 5 unknowns
- Category 3 (Convexity Verification): 7 unknowns
- Category 4 (GAMS Environment & Licensing): 5 unknowns
- Category 5 (Integration with Existing Code): 3 unknowns

**Estimated Research Time:** 30-38 hours (distributed across prep tasks)

---

## Table of Contents

1. [Category 1: GAMSLIB Access & Structure](#category-1-gamslib-access--structure)
2. [Category 2: Model Type Classification](#category-2-model-type-classification)
3. [Category 3: Convexity Verification](#category-3-convexity-verification)
4. [Category 4: GAMS Environment & Licensing](#category-4-gams-environment--licensing)
5. [Category 5: Integration with Existing Code](#category-5-integration-with-existing-code)
6. [Template for New Unknowns](#template-for-new-unknowns)
7. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: GAMSLIB Access & Structure

## Unknown 1.1: What is the URL structure for downloading individual GAMSLIB models?

### Priority
**Critical** - Required for download script development

### Assumption
GAMSLIB models can be downloaded directly from URLs with a predictable pattern like `https://www.gams.com/latest/gamslib_ml/libhtml/{model_name}.gms` or similar.

### Research Questions
1. Is there a direct download URL for each .gms file?
2. Does the URL require authentication or session cookies?
3. Are there rate limits or access restrictions?
4. Is the URL pattern consistent for all models?
5. Can models be accessed via API or only web scraping?

### How to Verify

**Test Case 1: Direct URL access**
```bash
curl -I "https://www.gams.com/latest/gamslib_ml/libhtml/trnsport.gms"
# Expected: 200 OK or redirect to download
```

**Test Case 2: Multiple model downloads**
- Download 3 different models
- Verify consistent URL pattern
- Check for rate limiting on rapid downloads

**Test Case 3: Authentication check**
- Access from clean browser session
- Verify no login required

### Risk if Wrong
- **No direct download:** May need web scraping, adding 4-6 hours complexity
- **Authentication required:** May need to use `gamslib` command instead
- **Rate limiting:** May need throttling in download script

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Direct .gms file downloads are available at: `https://www.gams.com/latest/gamslib_ml/{modelname}.{seq}`
- Example: `https://www.gams.com/latest/gamslib_ml/trnsport.1` returns the raw .gms file
- No authentication required - all models are publicly accessible
- No rate limiting observed during testing
- URL pattern is consistent across all models tested

**Evidence:**
```
$ curl -I "https://www.gams.com/latest/gamslib_ml/trnsport.1"
HTTP/2 200
content-type: text/plain
```

**Decision:** Web download is viable but `gamslib` command is preferred (see Unknown 1.2).

---

## Unknown 1.2: Can the `gamslib` command-line tool extract models locally?

### Priority
**Critical** - Alternative to web downloads

### Assumption
The GAMS installation includes a `gamslib` command that can extract models from the local GAMSLIB, avoiding web downloads entirely.

### Research Questions
1. Is `gamslib` included in the GAMS installation?
2. What is the command syntax for extracting a model?
3. Can we list all available models via command line?
4. Does it require any special permissions or license?
5. Are all GAMSLIB models available through this command?

### How to Verify

**Test Case 1: Command availability**
```bash
gamslib --help
# Expected: Help text showing usage
```

**Test Case 2: Model extraction**
```bash
gamslib trnsport /tmp/trnsport.gms
# Expected: Model file created
```

**Test Case 3: Model listing**
```bash
gamslib
# Expected: List of available models or directory listing
```

### Risk if Wrong
- **Command not available:** Must rely on web downloads
- **License restrictions:** Some models may require full license
- **Incomplete library:** Not all models may be accessible

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- `gamslib` command IS included with GAMS installation
- Location: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/gamslib`
- Command is on PATH and works without special permissions
- All 437 GAMSLIB models are accessible via this command
- No license restrictions for model extraction

**Evidence:**
```bash
$ gamslib trnsport
Copy ASCII : trnsport.gms

$ gamslib 2  # Extract by sequence number
Copy ASCII : blend.gms

$ gamslib -g  # Generate complete model list
Writing GAMS data for model to: gamslib.gms
```

**Syntax:**
```
gamslib [-lib glbfile] [-q(uiet)] <modelname | modelnum> [target]
```

**Decision:** Use `gamslib` command as primary extraction method. It's faster, more reliable, and doesn't require network access.

---

## Unknown 1.3: What metadata is available on GAMSLIB model pages?

### Priority
**High** - Required for catalog population

### Assumption
Each GAMSLIB model page contains structured metadata (model name, type, author, description, keywords) that can be parsed programmatically.

### Research Questions
1. What fields are consistently present on model pages?
2. Is the HTML structure consistent across all model pages?
3. Is model type (NLP, LP, MIP, etc.) explicitly stated?
4. Are there machine-readable metadata formats (JSON, XML)?
5. Is there a master list page with all models and metadata?

### How to Verify

**Test Case 1: Sample model page analysis**
- Visit 5 different model pages
- Document common metadata fields
- Check HTML structure consistency

**Test Case 2: Model type availability**
- Verify model type is visible on page
- Check if type is in HTML class/data attribute

**Test Case 3: Master list page**
- Check https://www.gams.com/latest/gamslib_ml/libhtml/
- Verify it lists all models with types

### Risk if Wrong
- **No structured metadata:** Manual classification required
- **Inconsistent pages:** Complex scraping logic needed
- **Type not available:** Must infer from model content

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Each model page displays structured metadata consistently
- Available metadata fields:
  - **Title:** Model name with sequence number (e.g., "A Transportation Problem (TRNSPORT,SEQ=1)")
  - **Type:** Problem classification (e.g., "Small Model of Type: LP")
  - **Description:** Problem description text
  - **Main file:** Link to .gms file
  - **Keywords:** Search terms
  - **References:** Academic citations
  - **Full source code:** Displayed inline on page
- Master index at `/latest/gamslib_ml/libhtml/` lists all 437 models with type and description
- HTML structure is consistent across model pages (DataTable format)
- No machine-readable JSON/XML format, but HTML is well-structured for parsing

**Evidence:**
```
Model page: https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html
- Title: "A Transportation Problem (TRNSPORT,SEQ=1)"
- Type: "Small Model of Type: LP"
- Keywords: "linear programming, transportation problem, scheduling"
```

**Decision:** Metadata is sufficient for catalog population. Model type can be parsed from page or from `$title` line in .gms file.

---

## Unknown 1.4: How many NLP and LP models exist in GAMSLIB?

### Priority
**High** - Validates 50+ model target

### Assumption
GAMSLIB contains at least 100 NLP and LP models combined, making the 50+ target easily achievable after filtering.

### Research Questions
1. What is the total number of models in GAMSLIB?
2. How many are classified as NLP?
3. How many are classified as LP?
4. How many are QCP (Quadratically Constrained Programs)?
5. What percentage are integer programs (excluded)?

### How to Verify

**Test Case 1: Count by type**
- Navigate GAMSLIB by model type
- Count NLP, LP, QCP, MIP, etc.

**Test Case 2: Validate sample**
- Select 10 random NLP models
- Verify they are truly NLP (not MINLP, etc.)

### Risk if Wrong
- **Fewer models:** May need to include QCP or relax criteria
- **Misclassification:** Declared NLP may actually be MINLP
- **Target unachievable:** May need to revise 50+ goal

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Total GAMSLIB models: 437
- NLP models: 49
- LP models: 57
- QCP models: 9
- **Combined NLP + LP + QCP: 115 models** (exceeds 50+ target)
- MIP models: 60 (excluded - integer variables)
- MINLP models: 21 (excluded - mixed integer nonlinear)
- Other excluded types: MCP (15), MPSGE (18), GAMS (19), DNLP (6), CNS (4), EMP (4), MIQCP (5), DECIS (5), MPEC (1), RMIQCP (2)

**Evidence:**
GAMSLIB index page at `https://www.gams.com/latest/gamslib_ml/libhtml/index.html` provides model counts by type. Verified by browsing type filters.

**Decision:** 115 candidate models significantly exceeds 50+ target. Focus on LP (all convex), NLP (requires verification), and QCP (requires verification).

---

## Unknown 1.5: Are there dependencies between GAMSLIB models ($include files)?

### Priority
**Medium** - Affects download completeness

### Assumption
Most GAMSLIB models are self-contained and don't require external data files or $include directives to run.

### Research Questions
1. Do any models use $include for external data?
2. Are included files available in GAMSLIB?
3. How to handle models with missing dependencies?
4. Should we skip or flag models with dependencies?
5. Is there documentation of model dependencies?

### How to Verify

**Test Case 1: Scan for $include**
```bash
# Download 10 sample models
grep -l '$include' *.gms
# Check if any use external includes
```

**Test Case 2: Dependency resolution**
- For models with $include, check if included file exists in GAMSLIB

### Risk if Wrong
- **Missing dependencies:** Models fail to run
- **Complex dependencies:** Adds download complexity
- **Incomplete corpus:** Some models unusable

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Tested first 50 GAMSLIB models - **NONE** contain `$include` or `$gdxin` statements
- Models are designed to be self-contained standalone examples
- All data is embedded inline using Set, Parameter, and Table statements
- Some models use `$call` for external program execution, but these are not data dependencies

**Evidence:**
```bash
$ cd /tmp/gamslib_test
$ for i in $(seq 1 50); do gamslib $i 2>/dev/null; done
$ grep -l '\$include\|\$gdxin' *.gms
# No matches - all 50 models are self-contained
```

**Models tested:** trnsport, blend, prodmix, whouse, jobt, sroute, diet, aircraft, prodsch, pdi, uimp, magic, ferts, fertd, mexss, mexsd, mexls, weapons, bid, process, chem, ship, linear, least, like, chance, sample, pindyck, zloof, vietman, alum, marco, chenery, pak, dinam, himmel16, robert, rdata, mine, orani, prolog, cube, chakra, andean, copper, shale, otpop, korpet, sarf, port

**Decision:** Treat GAMSLIB models as self-contained. No dependency resolution needed for download script.

---

## Unknown 1.6: Is the GAMSLIB web structure stable or version-dependent?

### Priority
**Low** - Affects long-term maintainability

### Assumption
The GAMSLIB web structure at `/latest/gamslib_ml/` remains stable across GAMS versions and updates.

### Research Questions
1. Does the URL structure change with GAMS versions?
2. Are older versions of GAMSLIB archived?
3. How frequently is GAMSLIB updated?
4. Will download scripts break on GAMS updates?

### How to Verify
- Check if `/47/gamslib_ml/` and `/latest/gamslib_ml/` have same structure
- Review GAMS release notes for GAMSLIB changes

### Risk if Wrong
- **URL changes:** Scripts may break on GAMS updates
- **Model changes:** Need version tracking

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- URL structure `/latest/gamslib_ml/` redirects to current GAMS version
- Version-specific URLs are available (e.g., `/47/`, `/51/`, `/52/`)
- URL pattern has been stable since at least GAMS 25.1
- Model naming is consistent across versions
- Sequence numbers are stable for existing models; new models added at end
- Version selector dropdown available on web interface for accessing different versions

**Evidence:**
```
Tested URLs:
- https://www.gams.com/latest/gamslib_ml/libhtml/ → Current version
- https://www.gams.com/51/gamslib_ml/libhtml/ → GAMS 51
- https://www.gams.com/47/gamslib_ml/libhtml/ → GAMS 47
All have same structure and navigation.
```

**Decision:** URL structure is stable. Use `/latest/` for current version access. Document GAMS version used for reproducibility.

---

# Category 2: Model Type Classification

## Unknown 2.1: How are GAMS model types declared in model files?

### Priority
**Critical** - Required for filtering models

### Assumption
GAMS model type is declared in the Model statement (e.g., `Model m /all/; Solve m using NLP minimizing obj;`) and can be parsed from the .gms file.

### Research Questions
1. Is model type always declared in `Solve` statement?
2. What are all valid model type keywords (NLP, LP, MIP, MINLP, MPEC, CNS, DNLP, MPSGE)?
3. Can a model have multiple solve statements with different types?
4. Are there models without explicit type declaration?
5. How to handle models with conditional type selection?

### How to Verify

**Test Case 1: Parse solve statement**
```gams
Solve myModel using NLP minimizing obj;
```
Extract: `NLP`

**Test Case 2: Verify all type codes**
- Download 20+ models of different types
- Confirm `using X` pattern is consistent

**Test Case 3: Edge cases**
- Check for `using MCP`, `using MPEC`, `using MPSGE`

### Risk if Wrong
- **Wrong parsing:** Models misclassified
- **Missing types:** Some models not categorized
- **False positives:** MINLP models classified as NLP

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Model type is declared in the `Solve` statement, NOT in the `Model` definition
- Syntax: `solve <model_name> using <type> [minimizing|maximizing] <variable>;`
- All valid model type keywords: LP, NLP, QCP, MIP, MINLP, MIQCP, MCP, MPEC, CNS, DNLP, EMP, MPSGE, RMIP, RMINLP, RMIQCP
- Type keyword is case-insensitive in GAMS
- A model CAN have multiple solve statements with different types
- No models found without explicit type declaration in solve statement

**Evidence:**
```gams
solve transport using lp minimizing z;      -- LP type
solve m using nlp minimizing r;             -- NLP type
solve qp7 using qcp minimizing z;           -- QCP type
solve hansen using mcp;                     -- MCP (no objective)
solve model1 using cns;                     -- CNS (no objective)
```

**Parsing Regex:**
```python
model_type_pattern = r'solve\s+\w+\s+.*?using\s+(\w+)'
```

**Decision:** Parse `using <type>` from solve statements. For models with multiple solves, use the first/primary solve type or flag for review.

---

## Unknown 2.2: Can we reliably distinguish convex NLP from non-convex NLP by type declaration?

### Priority
**High** - Core to convexity verification approach

### Assumption
Model type declaration (NLP vs DNLP) does not guarantee convexity - actual convexity must be verified by solving.

### Research Questions
1. Are all DNLPs non-convex by definition?
2. Can an NLP model be non-convex (yes, expected)?
3. Are there any NLP models that are guaranteed convex?
4. Should QCP be treated as potentially convex?
5. How do global solvers report convexity status?

### How to Verify

**Test Case 1: NLP convexity**
- Find NLP with non-convex function (e.g., sin, cos)
- Verify solver reports local optimum

**Test Case 2: LP convexity**
- Confirm all LPs report global optimum

**Test Case 3: QCP convexity**
- Check if convex QCPs report global optimum

### Risk if Wrong
- **False convex labels:** Non-convex models marked as convex
- **Missed models:** Convex models excluded incorrectly

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- **Cannot distinguish convex from non-convex NLP by type declaration alone**
- The `NLP` type encompasses both convex and non-convex problems
- LP is always convex by definition (linear objective + linear constraints)
- QCP is convex only if all quadratic forms are positive semidefinite
- DNLP is never convex (contains non-differentiable functions)
- Convexity must be verified empirically by solving

**Evidence:**
- `circle.gms` (NLP): Convex problem (minimize radius of enclosing circle)
- `qp1.gms`: QCP problem solved as NLP (`solve qp1 using nlp`)
- Local NLP solvers (CONOPT, IPOPT) report MODEL STATUS 2 (Locally Optimal) even for convex problems
- Only LP solver (CPLEX) reliably reports MODEL STATUS 1 (Optimal)

**Verification Strategy:**
1. LP → Always convex, MODEL STATUS 1 expected
2. NLP/QCP → Solve and check MODEL STATUS:
   - STATUS 1 → Solver proved global optimality → Convex
   - STATUS 2 → Local optimum only → Unknown (needs further analysis)

**Decision:** Type declaration is insufficient for convexity. Implement empirical verification via solve status. LP can be auto-classified as convex; NLP/QCP require verification.

---

## Unknown 2.3: What model types should definitely be excluded?

### Priority
**High** - Defines exclusion criteria

### Assumption
The following model types are unsuitable for MCP reformulation and should be excluded: MIP, MILP, MINLP, MPEC, MCP, MPSGE, CNS, DNLP.

### Research Questions
1. Why is each type unsuitable for MCP reformulation?
2. Are there edge cases where excluded types might work?
3. Is MPEC excluded because it's already MCP-like?
4. Should CNS (Constrained Nonlinear System) be excluded?
5. Are there sub-types or variants we're missing?

### How to Verify

**Test Case 1: Document exclusion rationale**
- MIP/MILP/MINLP: Integer variables incompatible with KKT
- MPEC: Already has complementarity constraints
- MPSGE: General equilibrium, specialized structure
- CNS: Square system, not optimization problem
- DNLP: Discontinuous, KKT conditions not applicable

### Risk if Wrong
- **Wrong exclusions:** Miss testable models
- **Wrong inclusions:** Include untestable models

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
The following model types should be **excluded** from the Sprint 13 corpus:

| Type | Count | Exclusion Rationale |
|------|-------|---------------------|
| MIP | 60 | Integer variables create non-convex feasible region |
| MINLP | 21 | Integer + nonlinear = non-convex |
| MIQCP | 5 | Integer + quadratic = non-convex |
| MCP | 15 | No objective function (equilibrium problem) |
| MPEC | 1 | Complementarity constraints are non-convex |
| CNS | 4 | No objective function (system of equations) |
| DNLP | 6 | Non-smooth functions (abs, min, max) violate differentiability |
| EMP | 4 | Meta-programming framework, not standard optimization |
| MPSGE | 18 | Specialized CGE equilibrium models |
| GAMS | 19 | Utility models without solve statements |
| DECIS | 5 | Stochastic programming framework |
| RMIP/RMINLP/RMIQCP | ~4 | Relaxed integer types still designed for integer problems |

**Total Excluded:** ~162 models

**Evidence:**
- MIP/MINLP/MIQCP: Integer variables fundamentally incompatible with KKT-based reformulation
- MCP/CNS: No objective to optimize - find equilibrium/solution to system
- MPEC: Contains complementarity constraints (already MCP-like)
- DNLP: Uses non-differentiable intrinsic functions; GAMS recommends reformulating as MINLP
- MPSGE: Domain-specific CGE modeling language

**Decision:** Exclude all listed types. Include only LP (57), NLP (49), and QCP (9) = 115 candidates.

---

## Unknown 2.4: How should QCP (Quadratically Constrained Programs) be handled?

### Priority
**Medium** - Potential corpus expansion

### Assumption
QCP models should be included if convex (convex quadratic constraints), excluded if non-convex.

### Research Questions
1. How many QCP models are in GAMSLIB?
2. Can we determine QCP convexity from model structure?
3. Does nlp2mcp support quadratic constraints?
4. Should QCP be in initial corpus or deferred?

### How to Verify
- Count QCP models in GAMSLIB
- Test nlp2mcp on simple QCP
- Verify convexity classification works

### Risk if Wrong
- **Missed opportunity:** Convex QCPs excluded
- **False positives:** Non-convex QCPs included

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- GAMSLIB contains **9 QCP models**
- QCP = Quadratically Constrained Program (quadratic objective and/or constraints)
- QCP is convex **only if** all quadratic forms are positive semidefinite (Q ⪰ 0)
- Some GAMSLIB QCP models are actually solved as NLP (e.g., `qp1.gms` uses `solve qp1 using nlp`)
- nlp2mcp should support QCP since quadratic functions are expressible in GAMS/MCP format

**Evidence:**
```gams
# qp7.gms - Uses QCP solve type
solve qp7 using qcp minimizing z;

# qp1.gms - QCP problem but solved as NLP
solve qp1 using nlp minimizing z;
```

**Convexity Verification for QCP:**
Same as NLP - solve and check MODEL STATUS:
- STATUS 1 → Convex (global optimum found)
- STATUS 2 → Unknown (may or may not be convex)

**Decision:** **Include QCP models** in Sprint 13 corpus. Apply same verification strategy as NLP. The 9 QCP models expand corpus to 115 candidates total.

---

## Unknown 2.5: How do models with RMINLP (Relaxed MINLP) type work?

### Priority
**Low** - Edge case handling

### Assumption
RMINLP models are continuous relaxations of MINLP and may be suitable for testing if they solve as NLP.

### Research Questions
1. Are there RMINLP models in GAMSLIB?
2. Can RMINLP be treated as NLP for our purposes?
3. Are there other relaxation types we should consider?

### How to Verify
- Search GAMSLIB for RMINLP models
- Test one with NLP solver

### Risk if Wrong
- **Missed models:** Some testable models excluded

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- RMINLP = Relaxed MINLP (continuous relaxation of mixed-integer nonlinear program)
- In RMINLP, integer/binary variables are treated as continuous within their bounds
- GAMSLIB has **0 models explicitly categorized as RMINLP** in the main index
- However, some models may use RMINLP internally for initialization or bounds computation
- Some models categorized elsewhere actually solve as different types (e.g., `ramsey.gms` solves as NLP)

**Evidence:**
```gams
# ramsey.gms - listed under various categories but solves as NLP
solve ramsey maximizing utility using nlp;
```

**Key Insight:** The library categorization may not match the actual solve type. Always parse the `solve ... using <type>` statement from the .gms file.

**RMIP/RMINLP/RMIQCP Handling:**
- These relaxed types are used for:
  1. Generating starting points for integer solvers
  2. Computing bounds in branch-and-bound
  3. Testing continuous relaxation of integer models
- They originate from integer problems and should be **excluded** from convex corpus

**Decision:** Exclude RMINLP/RMIP/RMIQCP types. If a model listed as RMINLP actually uses `solve ... using nlp`, evaluate based on actual solve type. Focus on models that are inherently continuous (LP, NLP, QCP).

---

# Category 3: Convexity Verification

## Unknown 3.1: What GAMS solver status codes indicate global vs local optimality?

### Priority
**Critical** - Core classification logic

### Assumption
GAMS MODEL STATUS = 1 indicates global optimum (convex), MODEL STATUS = 2 indicates local optimum only (non-convex).

### Research Questions
1. What is the complete list of MODEL STATUS codes?
2. What is the complete list of SOLVER STATUS codes?
3. Which combinations indicate definite convexity?
4. How do different solvers (CONOPT, IPOPT) report status?
5. Can a local solver prove global optimality for convex problems?

### How to Verify

**Test Case 1: LP model**
```gams
* Solve LP, check status
```
Expected: MODEL STATUS = 1 (Optimal)

**Test Case 2: Convex NLP**
```gams
* min x^2, check status
```
Expected: MODEL STATUS = 1 (Optimal)

**Test Case 3: Non-convex NLP**
```gams
* min sin(x), check status
```
Expected: MODEL STATUS = 2 (Locally Optimal)

### Risk if Wrong
- **Misclassification:** Non-convex models marked as convex
- **Pipeline corruption:** Wrong models enter testing corpus

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- MODEL STATUS codes range from 1-19, each with specific meaning
- MODEL STATUS 1 (Optimal) = Global optimum found (reliable for LP, not guaranteed for NLP with local solvers)
- MODEL STATUS 2 (Locally Optimal) = Local optimum found (NLP with local solver)
- MODEL STATUS 3 = Unbounded, 4 = Infeasible (exclude from corpus)
- SOLVER STATUS 1 = Normal Completion (required for valid result)
- **Critical insight:** Local NLP solvers (CONOPT, IPOPT), which use interior-point and SQP-type methods and are inherently local optimization algorithms, cannot prove global optimality even for convex problems

**Evidence:**
```
LP with CPLEX: MODEL STATUS = 1 (Optimal) → verified_convex
NLP with CONOPT: MODEL STATUS = 2 (Locally Optimal) → likely_convex (not proven)
```

**Decision:** LP with STATUS 1 = verified_convex. NLP/QCP with STATUS 1 or 2 = likely_convex (local solver cannot guarantee global optimality). See `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` for complete status code reference.

---

## Unknown 3.2: Which NLP solver should be used for convexity verification?

### Priority
**Critical** - Determines verification approach

### Assumption
CONOPT is the default NLP solver and sufficient for distinguishing global vs local optima in most cases.

### Research Questions
1. Which NLP solvers are available under demo license?
2. Does CONOPT correctly report local vs global status?
3. Would BARON (global solver) be better if available?
4. Should we use multiple solvers for validation?
5. Are there solver options that affect status reporting?

### How to Verify

**Test Case 1: CONOPT on convex problem**
```gams
Option NLP = CONOPT;
Solve ... using NLP ...
Display model.modelstat, model.solvestat;
```

**Test Case 2: CONOPT on non-convex problem**
- Same test with non-convex objective
- Verify STATUS = 2 (Locally Optimal)

### Risk if Wrong
- **Wrong solver:** May not correctly distinguish global/local
- **License issues:** Preferred solver not available
- **False positives:** Convex problems misclassified

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Available NLP solvers under demo license: CONOPT, IPOPT, MINOS, SNOPT, KNITRO
- **CONOPT recommended as primary solver** - default, robust, well-tested
- IPOPT as secondary if CONOPT fails
- Both CONOPT and IPOPT are **local solvers** - cannot prove global optimality
- BARON (global solver) has demo license limitations but could prove convexity definitively
- LP uses CPLEX (finds global optimum for linear programs)

**Evidence:**
```bash
$ gams solvers | grep -i nlp
NLP: CONOPT, IPOPT, MINOS, SNOPT, KNITRO
```

**Solver Selection:**
| Model Type | Solver | Capability |
|------------|--------|------------|
| LP | CPLEX | Proves global optimum |
| NLP/QCP | CONOPT | Finds local optimum (default) |
| NLP/QCP | IPOPT | Finds local optimum (secondary) |

**Decision:** Use CONOPT as primary NLP solver, CPLEX for LP. Local solvers cannot prove global optimality, so NLP models are classified as "likely_convex" rather than "verified_convex".

---

## Unknown 3.3: How long should convexity verification timeout be?

### Priority
**High** - Affects batch processing

### Assumption
60 seconds per model is sufficient for convexity verification; longer runs should be flagged as unknown.

### Research Questions
1. What is typical solve time for small NLP models?
2. What is typical solve time for medium NLP models?
3. At what point should we timeout vs wait?
4. Should timeout be model-size dependent?
5. How to handle timeout - exclude or retry with longer limit?

### How to Verify

**Test Case 1: Time 20 sample models**
- Record solve times
- Calculate mean, median, max

**Test Case 2: Identify outliers**
- Find models that take >60s
- Analyze why (size, structure, etc.)

### Risk if Wrong
- **Too short:** Many models flagged as unknown
- **Too long:** Batch processing takes forever

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- GAMSLIB models are designed as small examples - most solve in <1 second
- From GAMS_ENVIRONMENT_STATUS.md testing: solve times typically 0.01-0.1 seconds
- 60 seconds is **more than sufficient** for GAMSLIB models
- Timeout primarily guards against:
  - Pathological cases with numerical difficulties
  - Models that trigger infinite loops
  - License-related hangs

**Recommended Timeout Strategy:**
| Model Size | Timeout |
|------------|---------|
| Small (<100 vars) | 30 seconds |
| Medium (<1000 vars) | 60 seconds |
| Large (>1000 vars) | 120 seconds |

**Timeout Handling:**
- Mark as ERROR status
- Log for manual review
- Retry with longer timeout if needed (Sprint 14)

**Decision:** Use 60 seconds as default timeout. Models timing out are rare edge cases and should be flagged for manual review. Batch processing of 115 models should complete in <10 minutes even with conservative timeout.

---

## Unknown 3.4: How to parse objective value and solution status from GAMS .lst file?

### Priority
**High** - Required for result extraction

### Assumption
GAMS .lst files have consistent structure with MODEL STATUS, SOLVER STATUS, and objective value easily parseable.

### Research Questions
1. What is the exact format of status lines in .lst files?
2. Where is objective value reported?
3. Is format consistent across GAMS versions?
4. Are there variations for different solvers?
5. What encoding is used for .lst files?

### How to Verify

**Test Case 1: Parse sample .lst**
```python
# Pattern matching for:
# "MODEL STATUS: N"
# "SOLVER STATUS: N"
# "OBJECTIVE VALUE: X.XXX"
```

**Test Case 2: Multiple solvers**
- Compare CONOPT vs IPOPT .lst format

### Risk if Wrong
- **Parsing failures:** Can't extract results
- **Incorrect values:** Wrong objective captured
- **Version issues:** Breaks on different GAMS versions

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- .lst file format is consistent across solvers (CONOPT, IPOPT, CPLEX tested)
- Key lines appear in SOLVE SUMMARY section with consistent format
- Encoding is ASCII/UTF-8

**Exact Format:**
```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE                0.5000
```

**Parsing Regex Patterns:**
```python
# Solver status
solver_status_pattern = r'\*\*\*\* SOLVER STATUS\s+(\d+)\s+(.*)'

# Model status
model_status_pattern = r'\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*)'

# Objective value (handles scientific notation)
objective_pattern = r'\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)'
```

**Multiple Solves:**
- For models with multiple solve statements, parse ALL occurrences
- Use last occurrence for final result (or first for initial solve)

**Decision:** Patterns documented in `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` and `docs/testing/GAMS_ENVIRONMENT_STATUS.md`. Format is stable across GAMS versions and solvers.

---

## Unknown 3.5: How do non-convex models behave with local NLP solvers?

### Priority
**Medium** - Understanding expected behavior

### Assumption
Non-convex models solved with local solvers (CONOPT, IPOPT) will report MODEL STATUS = 2 (Locally Optimal).

### Research Questions
1. Do all non-convex models report local optimality?
2. Can a local solver find global optimum by chance and report it as global?
3. How do multi-start methods affect status reporting?
4. Are there non-convex models that report infeasibility?
5. How do degeneracy and multiple optima affect status?

### How to Verify

**Test Case 1: Known non-convex problems**
- Rosenbrock function
- Rastrigin function (if expressible in GAMS)

**Test Case 2: Multi-modal problems**
- Problems with multiple local optima
- Verify status = 2

### Risk if Wrong
- **False convex labels:** Non-convex problems mistakenly marked convex
- **Non-determinism:** Different runs give different classifications

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Non-convex models with local solvers typically return MODEL STATUS = 2 (Locally Optimal)
- Local solvers **never** report STATUS = 1 for NLP - they always report STATUS = 2
- Even **convex** NLP models return STATUS = 2 with local solvers (CONOPT, IPOPT)
- A local solver may find the global optimum by chance but cannot prove it
- Non-convex models may also return STATUS = 4 (Infeasible) if starting point is poor
- Multi-start is not default behavior - single solve from default starting point

**Key Insight:**
Both convex and non-convex NLP models return STATUS = 2 with local solvers. The status code **does not distinguish** between convex and non-convex problems when using local solvers.

**Implications for Classification:**
- LP with STATUS 1 → verified_convex (LP solver proves global optimum)
- NLP with STATUS 1 → unlikely (local solvers don't report this)
- NLP with STATUS 2 → likely_convex (cannot prove, but usable for testing)

**Decision:** Accept STATUS 2 for NLP/QCP as "likely_convex" since local solvers cannot distinguish convex from non-convex. Combine with heuristic detection (Tier 1) to flag obvious non-convex patterns.

---

## Unknown 3.6: Should we verify convexity with multiple starting points?

### Priority
**Medium** - Robustness of verification

### Assumption
Single solve is sufficient; multi-start verification is optional enhancement for Sprint 14+.

### Research Questions
1. Can different starting points lead to different status reports?
2. Would multi-start reduce false positives?
3. How many starting points would be sufficient?
4. What is the time cost of multi-start?
5. Should this be part of Sprint 13 or deferred?

### How to Verify
- Test one model with 3 different starting points
- Compare status and objective values

### Risk if Wrong
- **Inconsistent classification:** Same model classified differently
- **Missed non-convexity:** False convex label

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Different starting points CAN lead to different local optima for non-convex problems
- For convex problems, all starting points converge to same global optimum
- Multi-start would help detect non-convexity but adds complexity and time
- GAMSLIB models use default starting points (typically 0 or midpoint of bounds)

**Multi-Start Benefits:**
- If different starts → different objectives → definitely non-convex
- If different starts → same objective → likely convex (not proven)

**Time Cost:**
- 3 starting points = 3x solve time
- For 115 models at 1 second each = 5-6 minutes extra

**Sprint 13 Recommendation:**
- **Defer multi-start to Sprint 14+**
- Single solve is sufficient for initial classification
- GAMSLIB models are curated examples, most are well-posed
- Heuristic detection (Tier 1) catches obvious non-convex patterns

**Decision:** Sprint 13 uses single solve. Multi-start verification is enhancement for Sprint 14+ when validating MCP reformulation results.

---

## Unknown 3.7: How to handle models that are infeasible or unbounded?

### Priority
**Medium** - Edge case handling

### Assumption
Infeasible and unbounded models should be excluded from the convex corpus and flagged appropriately.

### Research Questions
1. What MODEL STATUS indicates infeasibility?
2. What MODEL STATUS indicates unboundedness?
3. Should infeasible models be retried with relaxed bounds?
4. Are there GAMSLIB models that are intentionally infeasible?
5. How to distinguish data errors from true infeasibility?

### How to Verify

**Test Case 1: Check GAMS status codes**
- Status 4: Infeasible
- Status 3: Unbounded

**Test Case 2: Create infeasible model**
- Verify status code
- Test exclusion logic

### Risk if Wrong
- **Wrong exclusions:** Fixable models excluded
- **Corpus errors:** Infeasible models included

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Infeasibility codes: MODEL STATUS 4 (Infeasible), 5 (Locally Infeasible), 6 (Intermediate Infeasible), 19 (Infeasible - No Solution)
- Unboundedness codes: MODEL STATUS 3 (Unbounded), 18 (Unbounded - No Solution)
- GAMSLIB models are designed to be solvable - infeasible/unbounded cases are rare
- Some GAMSLIB models may have parameter configurations that lead to infeasibility

**Handling Strategy:**
| MODEL STATUS | Name | Action |
|--------------|------|--------|
| 3 | Unbounded | Exclude from corpus |
| 4 | Infeasible | Exclude from corpus |
| 5 | Locally Infeasible | Exclude from corpus |
| 6 | Intermediate Infeasible | Exclude from corpus |
| 18 | Unbounded - No Solution | Exclude from corpus |
| 19 | Infeasible - No Solution | Exclude from corpus |

**No Retry Strategy:**
- GAMSLIB models should work with default parameters
- If infeasible, likely intentional or data issue
- Do NOT retry with relaxed bounds - just log and exclude

**Decision:** Exclude all infeasible/unbounded models from corpus. Log them separately for reference. No retry logic needed for Sprint 13. See `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` Section 3 for complete decision tree.

---

# Category 4: GAMS Environment & Licensing

## Unknown 4.1: What solvers are available under GAMS demo license?

### Priority
**Critical** - Determines verification capability

### Assumption
GAMS demo license includes CONOPT and/or IPOPT for NLP solving, sufficient for convexity verification.

### Research Questions
1. Which NLP solvers are included with demo license?
2. Are there size limits on demo license models?
3. Is PATH solver available for later MCP solving?
4. Are global solvers (BARON, ANTIGONE) available?
5. How to check current license capabilities?

### How to Verify

**Test Case 1: List available solvers**
```bash
gams license
gams solvers
```

**Test Case 2: Test NLP solver**
```bash
echo "Variables x; x.l=1; Equations e; e.. sqr(x)=e=1; Model m/e/; Solve m using NLP min x;" > /tmp/test.gms
gams /tmp/test.gms
```

### Risk if Wrong
- **Missing solvers:** Can't verify convexity
- **Size limits:** Can't test larger models
- **PATH missing:** Can't do later MCP solving

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
All major solvers are available under the GAMS Demo license with size restrictions.

**NLP Solvers (all tested successfully):**
| Solver | Status | Notes |
|--------|--------|-------|
| CONOPT | ✅ Available | Default NLP solver, demo license |
| CONOPT4 | ✅ Available | Latest CONOPT version |
| IPOPT | ✅ Available | Interior point optimizer |
| SNOPT | ✅ Available | Sequential quadratic programming |
| MINOS | ✅ Available | Legacy NLP solver |
| KNITRO | ✅ Available | Commercial-grade NLP |

**Global Solvers (all tested successfully):**
| Solver | Status | Notes |
|--------|--------|-------|
| BARON | ✅ Available | Returns MODEL STATUS 1 (Optimal) |
| ANTIGONE | ✅ Available | Returns global optimum confirmation |
| SCIP | ✅ Available | Open-source global solver |
| LINDOGLOBAL | ✅ Available | Returns MODEL STATUS 2 |

**MCP Solvers (all tested successfully):**
| Solver | Status | Notes |
|--------|--------|-------|
| PATH | ✅ Available | Default MCP solver |
| MILES | ✅ Available | Alternative MCP solver |

**LP/MIP Solvers:**
| Solver | Status | Notes |
|--------|--------|-------|
| CPLEX | ✅ Available | Default LP/MIP solver |
| CBC | ✅ Available | Open-source LP/MIP |
| GUROBI | ✅ Available | Commercial LP/MIP |
| HIGHS | ✅ Available | Open-source LP |

**Evidence:**
```bash
$ gams rbrock.gms nlp=CONOPT lo=0
**** MODEL STATUS      2 Locally Optimal

$ gams rbrock.gms nlp=BARON lo=0
**** MODEL STATUS      1 Optimal

$ gams test_mcp.gms mcp=PATH lo=0
**** MODEL STATUS      1 Optimal
```

**Decision:** Demo license provides comprehensive solver coverage. Use CONOPT as primary NLP solver, CPLEX for LP, PATH for MCP. Global solvers (BARON) available for convexity verification if needed.

---

## Unknown 4.2: What are the model size limits under demo license?

### Priority
**High** - May exclude some GAMSLIB models

### Assumption
Demo license allows models up to 300 variables and 300 equations, sufficient for most GAMSLIB examples.

### Research Questions
1. What are exact demo license limits (vars, eqs, nonzeros)?
2. What percentage of GAMSLIB models exceed these limits?
3. How to detect when limit is exceeded?
4. Is there a way to request expanded demo license?
5. Should we skip models exceeding limits or flag for manual testing?

### How to Verify

**Test Case 1: Create model at limit**
```gams
Set i /1*300/;
Variables x(i);
Equations e(i);
e(i).. x(i) =e= 0;
Model m /all/;
Solve m using NLP min sum(i, x(i));
```

**Test Case 2: Create model beyond limit**
- Same with 500 variables
- Observe error message

### Risk if Wrong
- **Can't test models:** Large GAMSLIB models excluded
- **Unexpected failures:** Size errors misinterpreted

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
Demo license has different limits for different model types:

**Model Size Limits:**
| Model Type | Max Rows | Max Columns | Tested |
|------------|----------|-------------|--------|
| LP | 2,000 | 2,000 | ✅ 1,999 vars works, 5,000 fails |
| NLP | 1,000 | 1,000 | ✅ 999 vars works, 1,000 fails |
| MIP | 2,000 | 2,000 | ✅ 500 int vars works |

**Evidence:**
```bash
# NLP at limit (999 variables + 1 objective = 1000 rows)
$ gams test_size_999.gms lo=3
**** Optimal solution. (1000 constraints, 1000 variables)

# NLP over limit (1000 variables + 1 objective = 1001 rows)
$ gams test_size_1000.gms lo=3
*** The model exceeds the demo license limits for nonlinear models 
    of more than 1000 rows or columns
*** Status: Terminated due to a licensing error

# LP at limit (1999 variables)
$ gams test_lp_2000.gms lo=3
Optimal solution found

# LP over limit (5000 variables)
$ gams test_lp_5000.gms lo=3
*** The model exceeds the demo license limits for linear models 
    of more than 2000 rows or columns
```

**GAMSLIB Impact:**
- GAMSLIB models are designed as **small teaching examples**
- Most models have <100 variables
- From test model set (Task 8): largest model has ~50 variables
- **No GAMSLIB models are expected to exceed demo limits**

**Error Detection:**
License errors produce:
- Exit code: 0 (misleading!)
- .lst file contains: `*** The model exceeds the demo license limits`
- .lst file contains: `*** Status: Terminated due to a licensing error`

**Decision:** Demo limits are sufficient for GAMSLIB corpus. LP limit of 2,000 and NLP limit of 1,000 far exceed typical GAMSLIB model sizes. Add license error detection to verification script.

---

## Unknown 4.3: Is GAMS installation path consistent across systems?

### Priority
**Medium** - Affects script portability

### Assumption
GAMS is on system PATH and `gams` command is available from any directory.

### Research Questions
1. Is GAMS installed to PATH on macOS?
2. What about Linux and Windows installations?
3. Should scripts assume GAMS is on PATH or search for it?
4. Are there environment variables for GAMS location?
5. How to provide graceful error if GAMS not found?

### How to Verify

**Test Case 1: Check PATH**
```bash
which gams
gams --version
```

**Test Case 2: Check environment variables**
```bash
env | grep -i gams
```

### Risk if Wrong
- **Scripts fail:** GAMS not found
- **Portability issues:** Works on one system, fails on another

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- GAMS IS on system PATH on macOS after standard installation
- Location: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams`
- `which gams` returns the path successfully
- `gamslib` command is also on PATH
- No environment variables needed for standard usage

**Evidence:**
```bash
$ which gams
/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams

$ which gamslib
/Library/Frameworks/GAMS.framework/Versions/51/Resources/gamslib
```

**Cross-Platform Notes:**
- macOS: `/Library/Frameworks/GAMS.framework/Versions/XX/Resources/`
- Linux: Typically `/opt/gams/` or user directory
- Windows: Typically `C:\GAMS\XX\`

**Decision:** Scripts should use `which gams` to verify availability. Provide clear error message if GAMS not found on PATH.

---

## Unknown 4.4: How to run GAMS non-interactively for batch processing?

### Priority
**High** - Required for automation

### Assumption
GAMS can be run non-interactively with `gams model.gms` and exit codes indicate success/failure.

### Research Questions
1. What exit codes does GAMS return?
2. How to suppress interactive prompts?
3. How to capture stdout/stderr?
4. How to specify output directory for .lst files?
5. Are there useful command-line options for batch mode?

### How to Verify

**Test Case 1: Run and check exit code**
```bash
gams model.gms
echo $?
# Expected: 0 for success
```

**Test Case 2: Batch options**
```bash
gams model.gms lo=0 o=/dev/null
# lo=0: listing output level
# o: output file
```

### Risk if Wrong
- **Interactive prompts:** Script hangs
- **Wrong exit codes:** Success/failure misinterpreted
- **Output scattered:** Can't find .lst files

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- GAMS runs non-interactively by default with `gams model.gms`
- No interactive prompts occur during batch execution
- Exit codes: 0 = normal completion, 2 = compilation error
- **Important:** Exit code 0 does NOT mean optimal solution - must check MODEL STATUS in .lst file

**Evidence:**
```bash
# Normal execution
$ gams convex_nlp.gms lo=3
Exit code: 0

# Syntax error
$ gams syntax_error.gms lo=3
Exit code: 2
```

**Key Command-Line Options:**
| Option | Description |
|--------|-------------|
| `lo=N` | Log output level (0=none, 3=summary, 4=verbose) |
| `o=file` | Specify output .lst file path |
| `NLP=solver` | Select NLP solver (CONOPT, IPOPT, etc.) |
| `LP=solver` | Select LP solver |

**Batch Execution Pattern:**
```bash
gams model.gms lo=3 o=output.lst
if [ $? -eq 0 ]; then
    grep "MODEL STATUS" output.lst
fi
```

**Decision:** Use `gams model.gms lo=3` for batch processing. Always check MODEL STATUS in .lst file, not just exit code.

---

## Unknown 4.5: How does GAMS handle errors in model files?

### Priority
**Medium** - Error handling design

### Assumption
GAMS produces clear error messages in .lst file when model has syntax or semantic errors.

### Research Questions
1. Where are compile errors reported?
2. Where are execution errors reported?
3. What exit code for compilation errors?
4. What exit code for solve failures?
5. How to distinguish error types?

### How to Verify

**Test Case 1: Syntax error**
```gams
Variables x
Equations e;  * Missing semicolon above
```
Check .lst for error location

**Test Case 2: Semantic error**
```gams
Variable x;
Equation e;
e.. x + y =e= 0;  * y undefined
```
Check .lst for error message

### Risk if Wrong
- **Can't detect errors:** Failed models not flagged
- **Wrong classification:** Error models in corpus

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
- Compilation errors: Exit code 2, errors reported in .lst file with line numbers
- Execution errors: Exit code varies, errors in .lst file
- Solve failures (infeasible, unbounded): Exit code 0, but MODEL STATUS indicates issue
- Error messages include file path, line number, and error code

**Evidence - Syntax Error:**
```
*** Error 409 in /tmp/gams_test/syntax_error.gms
    Unrecognizable item - skip to find a new statement
Exit code: 2
```

**Evidence - Infeasible Model:**
```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      4 Infeasible
Exit code: 0  (must check MODEL STATUS!)
```

**Error Detection Strategy:**
1. Check exit code first (non-zero = compilation/system error)
2. If exit code 0, parse .lst for SOLVER STATUS and MODEL STATUS
3. SOLVER STATUS != 1 indicates solver problem
4. MODEL STATUS in {3, 4, 5, 6, ...} indicates solve issue

**Decision:** Implement two-stage error detection: exit code check + .lst file parsing. Never trust exit code 0 alone.

---

# Category 5: Integration with Existing Code

## Unknown 5.1: What GAMSLIB work exists from EPIC 2?

### Priority
**High** - Avoid duplicate work

### Assumption
EPIC 2 Sprints 7-12 include GAMSLIB-related code, scripts, and research that can be reused.

### Research Questions
1. What GAMSLIB scripts exist in the codebase?
2. What test fixtures from GAMSLIB exist?
3. What research documents cover GAMSLIB?
4. What lessons learned are documented?
5. What parsing success rates were achieved?

### How to Verify

**Test Case 1: Find existing files**
```bash
find . -name "*gamslib*" -o -name "*GAMSLIB*"
find docs -name "*.md" -exec grep -l -i "gamslib" {} \;
```

**Test Case 2: Review EPIC 2 status**
- Check `docs/status/GAMSLIB_CONVERSION_STATUS.md`
- Review Sprint 11-12 retrospectives

### Risk if Wrong
- **Duplicate effort:** Rebuild existing functionality
- **Missed learnings:** Repeat past mistakes

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**
Extensive GAMSLIB infrastructure exists from EPIC 2 Sprints 6-12:

**Scripts:**
- `scripts/download_gamslib_nlp.sh` - Downloads models from GAMS website with retry logic, validation
- `scripts/ingest_gamslib.py` - Parses models, generates JSON reports, creates dashboards

**Test Fixtures:**
- `tests/fixtures/gamslib/` - 10 Tier 1 NLP models (circle, himmel16, hs62, mathopt1, maxmin, mhw4d, mhw4dx, mingamma, rbrock, trig)
- All 10 models parse successfully (100% parse rate achieved in Sprint 8)

**Research Documents:**
- `docs/research/gamslib_parse_errors.md` - Sprint 6 baseline (0% → 100% parse rate)
- `docs/research/gamslib_kpi_definitions.md` - 4-KPI framework (parse%, convert%, solve%, e2e%)
- `docs/research/ingestion_schedule.md` - Manual ingestion planning
- `docs/status/GAMSLIB_CONVERSION_STATUS.md` - Current status dashboard

**Lessons Learned:**
- Initial 0% parse rate due to grammar gaps (variable .l assignments, compiler directives, set ranges)
- All grammar issues fixed in Sprint 6-8
- KPI framework provides solid metrics foundation
- Scripts are well-structured and extensible

**Decision:** Sprint 13 can reuse download script (extend for 115 models), ingestion script (add convexity verification), and KPI framework. See `docs/research/GAMSLIB_EXISTING_WORK_REVIEW.md` for full details.

---

## Unknown 5.2: How does nlp2mcp currently parse model type declarations?

### Priority
**Medium** - Integration with existing parser

### Assumption
nlp2mcp parser already handles `Solve ... using NLP ...` statements and can extract model type.

### Research Questions
1. Does parser extract model type from Solve statement?
2. Is model type stored in IR?
3. Can we query model type after parsing?
4. What happens with unsupported model types (MIP, etc.)?
5. Is there existing code to filter by model type?

### How to Verify

**Test Case 1: Parse and check type**
```python
from src.ir.parser import parse_model_file
model = parse_model_file("test.gms")
print(model.model_type)  # or similar accessor
```

### Risk if Wrong
- **Parser changes needed:** May need to extend parser
- **Type not available:** Must parse Solve statement separately

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**

**1. Grammar DOES parse solver_type:**
From `src/gams/gams_grammar.lark`:
```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI     -> solve
          | "Solve"i ID "using"i solver_type obj_sense ID SEMI     -> solve

solver_type: /(?i:nlp|dnlp|minlp|mip|lp|mcp|cns|qcp|rmip|rminlp)\b/
```
Supports: NLP, DNLP, MINLP, MIP, LP, MCP, CNS, QCP, RMIP, RMINLP

**2. GAP: solver_type is NOT stored in ModelIR:**
From `src/ir/model_ir.py`:
```python
@dataclass
class ModelIR:
    declared_model: str | None = None
    model_equations: list[str] = field(default_factory=list)
    model_uses_all: bool = False
    model_name: str | None = None
    objective: ObjectiveIR | None = None
    # NOTE: solver_type field is MISSING!
```

**3. Cannot query model type after parsing:**
- `model.solver_type` does not exist
- Type is parsed and discarded during transformation

**4. Unsupported types:**
- All types in grammar are parsed without error
- No filtering by type occurs during parsing

**Impact on Sprint 13:**
- Must add `solver_type: str | None = None` to ModelIR
- Must update transformer to populate solver_type from parse tree
- Estimated fix: 1-2 hours

**Decision:** Grammar works correctly. Need to extend ModelIR and transformer to store solver_type. See `docs/research/GAMSLIB_EXISTING_WORK_REVIEW.md` Section 4 for details.

---

## Unknown 5.3: Should the JSON catalog use existing nlp2mcp data structures?

### Priority
**Low** - Design decision

### Assumption
JSON catalog is a standalone data structure, separate from nlp2mcp IR, for maximum flexibility.

### Research Questions
1. Are there existing data classes for model metadata?
2. Would reusing existing structures reduce code?
3. What serialization is already supported?
4. Should catalog be compatible with existing test infrastructure?
5. Is there existing JSON schema in the project?

### How to Verify
- Review `src/ir/` for existing data structures
- Check for JSON serialization utilities
- Review test fixture organization

### Risk if Wrong
- **Incompatibility:** Catalog doesn't integrate well
- **Duplicate structures:** Maintain two representations

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:**

**1. Existing data classes for model metadata:**
- `scripts/ingest_gamslib.py` defines `ModelResult` and `IngestionReport` dataclasses
- `src/ir/diagnostics.py` defines `DiagnosticReport` with stage metrics
- These are separate from ModelIR (internal representation)

**2. JSON serialization already supported:**
- Uses `dataclasses.asdict()` for serialization (standard library)
- No external dependencies (dataclasses_json, pydantic not used)
- Pattern: `json.dump(asdict(report), f, indent=2)`

**3. Existing pattern from ingest_gamslib.py:**
```python
@dataclass
class ModelResult:
    model_name: str
    gms_file: str
    parse_status: str  # "SUCCESS" or "FAILED"
    parse_error: str | None = None
    parse_error_type: str | None = None
    parse_progress_percentage: float | None = None
    ...

@dataclass
class IngestionReport:
    sprint: str
    total_models: int
    models: list[ModelResult]
    kpis: dict[str, Any]
```

**4. Recommendation:**
- **Use standalone catalog structure** (not tied to ModelIR)
- ModelIR is optimized for internal transformation, not external metadata
- Follow `ModelResult` pattern with dedicated dataclasses
- Use `dataclasses.asdict()` for JSON serialization
- This provides flexibility to evolve catalog independently

**5. No existing JSON schema validation:**
- Current approach uses Python dataclasses without formal JSON Schema
- Sprint 14 can add JSON Schema validation if needed

**Decision:** Create standalone catalog dataclasses following the `ModelResult` pattern. Keep catalog independent of ModelIR for flexibility. See `docs/research/GAMSLIB_EXISTING_WORK_REVIEW.md` Section 4.3 for details.

---

# Template for New Unknowns

Use this template when adding newly discovered unknowns during the sprint:

```markdown
## Unknown X.N: [Brief description]

### Priority
**[Critical/High/Medium/Low]** - [Brief justification]

### Assumption
[What we currently believe/assume]

### Research Questions
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]

### How to Verify
[Specific test cases or experiments]

### Risk if Wrong
[Impact on sprint if assumption is incorrect]

### Estimated Research Time
[Hours]

### Owner
[Team or individual]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

# Confirmed Knowledge

*(Move verified unknowns here with findings)*

---

# Next Steps

1. **Before Sprint 13 Day 1:** Verify all Critical and High priority unknowns
2. **Prep Task Assignments:** See Task-to-Unknown Mapping below
3. **Daily Review:** Check for new unknowns during implementation
4. **Sprint 13 End:** Complete retrospective with unknown resolution summary

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from PREP_PLAN.md) verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Research GAMSLIB Structure and Access | 1.1, 1.2, 1.3, 1.5, 1.6 | URL patterns, gamslib command, metadata, dependencies |
| Task 3: Validate GAMS Local Environment | 4.3, 4.4, 4.5 | PATH availability, batch mode, error handling |
| Task 4: Survey GAMSLIB Model Types | 1.4, 2.1, 2.2, 2.3, 2.4, 2.5 | Model counts, type declarations, exclusion criteria |
| Task 5: Research Convexity Verification | 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7 | Status codes, solver selection, parsing, edge cases |
| Task 6: Review Existing GAMSLIB Work | 5.1, 5.2, 5.3 | Existing code, parser capabilities, data structures |
| Task 7: Design JSON Catalog Schema | 5.3 | Schema design, data structure decisions |
| Task 8: Create Test Model Set | 1.5, 2.1, 3.5 | Tests dependency handling, type parsing, non-convex behavior |
| Task 9: Audit GAMS License Capabilities | 4.1, 4.2 | Solver availability, size limits |
| Task 10: Plan Sprint 13 Schedule | All | Integrates all verified unknowns into plan |

### Coverage Summary

- **Category 1 (GAMSLIB Access):** Covered by Tasks 2, 8
- **Category 2 (Model Types):** Covered by Tasks 4, 8
- **Category 3 (Convexity Verification):** Covered by Tasks 5, 8
- **Category 4 (GAMS Environment):** Covered by Tasks 3, 9
- **Category 5 (Integration):** Covered by Tasks 6, 7

### Unknowns Not Directly Covered by Prep Tasks

All 26 unknowns are covered by at least one prep task. Task 10 integrates findings from all other tasks into the final Sprint 13 plan.

---

## Changelog

- **2025-12-29:** Initial Sprint 13 Known Unknowns document created with 26 unknowns
