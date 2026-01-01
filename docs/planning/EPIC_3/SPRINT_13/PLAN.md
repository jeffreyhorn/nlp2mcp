# Sprint 13 Plan: GAMSLIB Discovery, Download Infrastructure & Convexity Verification Foundation

**Sprint Duration:** 10 working days  
**Estimated Effort:** 29-39 hours  
**Risk Level:** LOW (infrastructure work with clear deliverables)  
**Created:** December 31, 2025

---

## Executive Summary

Sprint 13 initiates EPIC 3, establishing the infrastructure to discover, download, and classify GAMSLIB models for MCP reformulation testing. This sprint builds on extensive prep work (Tasks 1-9) that verified all 26 unknowns and confirmed the technical approach is sound.

**Key Outcomes:**
- 50+ NLP/LP models cataloged from GAMSLIB
- Automated download script for model extraction
- Convexity verification framework classifying models by solver status
- JSON catalog structure for tracking model pipeline status

---

## Sprint Goals

### Primary Goals (from PROJECT_PLAN.md)
1. **Model Discovery:** Identify and catalog 50+ NLP/LP candidate models from GAMSLIB
2. **Download Infrastructure:** Create scripts to download models from GAMS Model Library
3. **Convexity Verification Foundation:** Build system to verify models are convex via solver status

### Success Criteria
- [ ] 50+ NLP/LP candidate models identified and cataloged
- [ ] Download script successfully downloads models with proper error handling
- [ ] Convexity script can execute GAMS models and classify by solver status
- [ ] JSON catalog contains metadata for all discovered models
- [ ] Model type research documented with clear exclusion rationale
- [ ] All scripts have basic error handling

---

## Prep Task Findings Integration

### From Task 1-2: GAMSLIB Access
- **Primary Method:** Use `gamslib` command-line tool (fast, reliable, no network needed)
- **Backup Method:** Web download at `https://www.gams.com/latest/gamslib_ml/{name}.{seq}`
- **Total Models:** 437 in GAMSLIB
- **Models are self-contained:** No $include dependencies found

### From Task 3-4: Model Types & Environment
- **Target Models:** LP (57), NLP (49), QCP (9) = **115 candidates**
- **Excluded Types:** MIP, MINLP, MIQCP, MCP, MPEC, CNS, DNLP, EMP, MPSGE, GAMS, DECIS
- **GAMS on PATH:** Confirmed at `/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams`
- **Batch Mode:** Use `gams model.gms lo=3`, parse .lst file for status

### From Task 5: Convexity Verification Design
- **LP Models:** Automatically `verified_convex` (MODEL STATUS 1 with CPLEX)
- **NLP/QCP Models:** Classified as `likely_convex` (MODEL STATUS 1 or 2 with local solvers)
- **Timeout:** 60 seconds sufficient for GAMSLIB models
- **Parsing Patterns:**
  ```
  **** SOLVER STATUS     1 Normal Completion
  **** MODEL STATUS      2 Locally Optimal
  **** OBJECTIVE VALUE                0.5000
  ```

### From Task 6-7: Existing Work & Schema
- **Reusable Scripts:** `scripts/download_gamslib_nlp.sh`, `scripts/ingest_gamslib.py`
- **Test Fixtures:** 10 Tier 1 models in `tests/fixtures/gamslib/`
- **Schema Ready:** Catalog schema designed with 12 fields, extension points for Sprint 14
- **Gap to Address:** Add `solver_type` to ModelIR (1-2 hours)

### From Task 8-9: Test Models & License
- **Test Set:** 13 models in `tests/fixtures/gamslib_test_models/`
- **License Limits:** NLP: 1,000 rows/cols, LP: 2,000 rows/cols (sufficient for GAMSLIB)
- **Solvers Available:** CONOPT, IPOPT, BARON, ANTIGONE, PATH, CPLEX, CBC

---

## Day-by-Day Plan

### Days 1-2: Model Discovery & Catalog Creation

#### Day 1: Directory Structure & Catalog Schema Implementation
**Effort:** 3-4 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Create `data/gamslib/` directory structure | Directory tree with .gitignore | ✅ |
| 1.2 | Create `scripts/gamslib/` directory | Script location ready | ✅ |
| 1.3 | Implement catalog dataclasses | `scripts/gamslib/catalog.py` | ✅ |
| 1.4 | Create empty catalog.json with schema | `data/gamslib/catalog.json` | ✅ |
| 1.5 | Write catalog unit tests | `tests/test_gamslib_catalog.py` | ✅ |

**Checkpoint:** Directory structure exists, catalog schema implemented ✅ **COMPLETE**

#### Day 2: Model List Population
**Effort:** 3-4 hours

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 2.1 | Create model discovery script | `scripts/gamslib/discover_models.py` | ✅ |
| 2.2 | Parse GAMSLIB index for LP/NLP/QCP models | 219 candidate entries | ✅ |
| 2.3 | Extract metadata (name, seq#, type, description) | Catalog populated | ✅ |
| 2.4 | Filter by inclusion criteria | 219 models in catalog | ✅ |
| 2.5 | Generate discovery report | `data/gamslib/discovery_report.md` | ✅ |

**Checkpoint Day 2:** Catalog contains 50+ candidate model entries ✅ **COMPLETE (219 models)**

---

### Days 3-4: Download Infrastructure

#### Day 3: Download Script Development
**Effort:** 4-5 hours

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 3.1 | Create download script | `scripts/gamslib/download_models.py` | ✅ |
| 3.2 | Implement `gamslib` command wrapper | Extract models to `data/gamslib/raw/` | ✅ |
| 3.3 | Add idempotent download (skip existing) | Efficient re-runs | ✅ |
| 3.4 | Add error handling and logging | Robust extraction | ✅ |
| 3.5 | Update catalog with download status | Status tracking | ✅ |

**Checkpoint Day 3:** Download script functional, can extract models ✅ **COMPLETE**

#### Day 4: Full Model Set Download & Validation
**Effort:** 2-3 hours

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 4.1 | Download all 50+ candidate models | Models in `data/gamslib/raw/` | ✅ |
| 4.2 | Validate file integrity | All .gms files present | ✅ |
| 4.3 | Handle edge cases (missing, errors) | Error log generated | ✅ |
| 4.4 | Update catalog with file sizes | Metadata complete | ✅ |
| 4.5 | Create download summary report | `data/gamslib/download_report.md` | ✅ |

**Checkpoint Day 4:** All 219 models downloaded, validated, catalog updated ✅ **COMPLETE**

---

### Days 5-6: Convexity Verification Foundation

#### Day 5: GAMS Execution Framework
**Effort:** 5-6 hours

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 5.1 | Create verification script | `scripts/gamslib/verify_convexity.py` | ✅ |
| 5.2 | Implement GAMS execution wrapper | Run models via subprocess | ✅ |
| 5.3 | Add .lst file parsing | Extract MODEL/SOLVER STATUS | ✅ |
| 5.4 | Add timeout handling (60s default) | Prevent hangs | ✅ |
| 5.5 | Capture solve results (status, objective, time) | Result dataclass | ✅ |

**Checkpoint Day 5:** GAMS execution framework ready ✅ **COMPLETE**

#### Day 6: Classification Logic & Initial Run
**Effort:** 3-4 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 6.1 | Implement classification logic | Status → convexity mapping |
| 6.2 | Handle LP models (auto verified_convex) | LP classification |
| 6.3 | Handle NLP/QCP models (likely_convex) | NLP classification |
| 6.4 | Run verification on test models (13) | Validate pipeline |
| 6.5 | Update catalog with convexity results | Status recorded |

**Checkpoint:** Verification working on test model set

---

### Days 7-8: Integration & Testing

#### Day 7: Integration Testing & Bug Fixes
**Effort:** 3-4 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 7.1 | Run full pipeline on 50+ models | End-to-end test |
| 7.2 | Fix bugs discovered during testing | Bug fixes |
| 7.3 | Handle edge cases | Robust handling |
| 7.4 | Generate convexity summary report | Classification statistics |
| 7.5 | Review and update catalog | Complete metadata |

**Checkpoint Day 7:** Convexity verification working

#### Day 8: Documentation & Checkpoint Review
**Effort:** 2-3 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 8.1 | Create `docs/research/GAMSLIB_MODEL_TYPES.md` | Model type documentation |
| 8.2 | Document exclusion rationale | Clear criteria |
| 8.3 | Update script docstrings | Code documentation |
| 8.4 | Create usage examples | Example commands |
| 8.5 | Review against acceptance criteria | Checkpoint validation |

**Checkpoint:** Documentation complete, scripts documented

---

### Days 9-10: Buffer & Polish

#### Day 9: Address Issues & Refinements
**Effort:** 2-3 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 9.1 | Address issues from Day 7-8 testing | Bug fixes |
| 9.2 | Improve error messages | User-friendly output |
| 9.3 | Add edge case handling | Robustness |
| 9.4 | Optimize performance if needed | Efficiency |
| 9.5 | Update tests for new cases | Test coverage |

#### Day 10: Final Documentation & Sprint Review Prep
**Effort:** 2-3 hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 10.1 | Final catalog review | Data quality check |
| 10.2 | Create sprint summary report | Status overview |
| 10.3 | Update CHANGELOG.md | Release notes |
| 10.4 | Prepare sprint retrospective notes | Lessons learned |
| 10.5 | Final acceptance criteria review | All criteria met |

**Checkpoint Day 10:** All acceptance criteria met

---

## Checkpoints

| Checkpoint | Day | Criteria | Success Indicator |
|------------|-----|----------|-------------------|
| **Catalog Populated** | 2 | 50+ model entries in catalog.json | Count >= 50 |
| **Download Functional** | 3 | Download script extracts models | All test models downloaded |
| **Execution Framework** | 5 | GAMS execution framework ready | Can run and parse .lst files |
| **Verification Working** | 7 | Convexity classification running | Test models classified |
| **Sprint Complete** | 10 | All acceptance criteria met | 100% criteria checked |

---

## Risk Identification & Mitigation

### Risk 1: GAMSLIB Access Issues
- **Probability:** Low (already verified in Task 2)
- **Impact:** Medium (delays model discovery)
- **Mitigation:** Use `gamslib` command as primary method; web download as backup
- **Status:** MITIGATED (verified in prep tasks)

### Risk 2: Model Type Misclassification
- **Probability:** Low (clear criteria defined)
- **Impact:** Medium (wrong models in corpus)
- **Mitigation:** Parse `solve ... using <type>` from files; double-check against catalog
- **Status:** MITIGATED (parsing pattern verified in Task 5)

### Risk 3: GAMS License Limits
- **Probability:** Very Low (limits far exceed needs)
- **Impact:** Low (skip large models)
- **Mitigation:** NLP limit 1,000, LP limit 2,000; GAMSLIB models are <100 variables
- **Status:** MITIGATED (verified in Task 9)

### Risk 4: Solver Availability
- **Probability:** Very Low (all solvers verified)
- **Impact:** Medium (can't verify convexity)
- **Mitigation:** CONOPT, IPOPT, BARON all available under demo license
- **Status:** MITIGATED (verified in Task 9)

### Risk 5: Non-Convex Models in Corpus
- **Probability:** Medium (some NLP models may be non-convex)
- **Impact:** Low (classification handles this)
- **Mitigation:** Use `likely_convex` classification; defer multi-start to Sprint 14
- **Status:** ACCEPTED (by design)

---

## Acceptance Criteria Checklist

### Model Discovery
- [ ] 50+ NLP/LP candidate models identified
- [ ] Models cataloged with metadata (name, type, seq#, description)
- [ ] Exclusion criteria applied correctly

### Download Script
- [ ] Successfully downloads models from GAMSLIB
- [ ] Handles errors gracefully (missing models, network issues)
- [ ] Idempotent operation (skip existing files)
- [ ] Updates catalog with download status

### Convexity Verification
- [ ] Executes GAMS models locally
- [ ] Captures solver output (MODEL STATUS, SOLVER STATUS)
- [ ] Classifies by solver status (verified_convex, likely_convex, excluded)
- [ ] Handles timeouts and errors

### Catalog Structure
- [ ] JSON catalog with defined schema
- [ ] Contains metadata for all discovered models
- [ ] Extensible for Sprint 14 additions

### Documentation
- [ ] `docs/research/GAMSLIB_MODEL_TYPES.md` created
- [ ] Exclusion rationale documented
- [ ] Scripts have docstrings and usage examples

### Quality
- [ ] Scripts have error handling
- [ ] Basic tests exist for core functionality

---

## Dependencies

### External Dependencies
- GAMS 51.3.0 installed and on PATH (verified)
- Demo license active (verified, no expiration)
- `gamslib` command available (verified)

### Internal Dependencies
- Prep tasks 1-9 complete (verified)
- Test model set available at `tests/fixtures/gamslib_test_models/` (verified)
- Catalog schema designed (verified)

---

## Resource Allocation

| Component | Estimated Hours | Days |
|-----------|-----------------|------|
| Model Discovery & Catalog | 6-8 hours | Days 1-2 |
| Download Infrastructure | 6-8 hours | Days 3-4 |
| Convexity Verification | 8-10 hours | Days 5-6 |
| Integration & Testing | 5-7 hours | Days 7-8 |
| Buffer & Polish | 4-6 hours | Days 9-10 |
| **Total** | **29-39 hours** | **10 days** |

---

## Known Unknowns Status

All 26 unknowns from `KNOWN_UNKNOWNS.md` have been verified:

| Category | Count | Status |
|----------|-------|--------|
| Category 1: GAMSLIB Access & Structure | 6 | ✅ All Verified |
| Category 2: Model Type Classification | 5 | ✅ All Verified |
| Category 3: Convexity Verification | 7 | ✅ All Verified |
| Category 4: GAMS Environment & Licensing | 5 | ✅ All Verified |
| Category 5: Integration with Existing Code | 3 | ✅ All Verified |
| **Total** | **26** | **✅ 100% Verified** |

**Key Verified Findings:**
- `gamslib` command is preferred extraction method
- 115 candidate models (LP: 57, NLP: 49, QCP: 9)
- Local solvers return STATUS 2 for NLP (use `likely_convex` classification)
- Demo license limits sufficient (NLP: 1,000, LP: 2,000)
- All required solvers available

---

## Post-Sprint Handoff

### To Sprint 14
- Catalog with 50+ models and convexity status
- Download and verification scripts
- Gap: Add `solver_type` to ModelIR (deferred, 1-2 hours)
- Gap: Multi-solver validation (optional enhancement)

### Documentation Updates
- `docs/research/GAMSLIB_MODEL_TYPES.md` - Model type reference
- `data/gamslib/catalog.json` - Model catalog
- Script documentation and examples

---

## Changelog

- **2025-12-31:** Sprint 13 Plan created, incorporating all prep task findings
