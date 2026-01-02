# Sprint 14 Detailed Plan

**Sprint:** 14  
**Duration:** 10 working days  
**Goal:** Complete Convexity Verification & JSON Database Infrastructure  
**Status:** READY FOR EXECUTION

---

## Executive Summary

Sprint 14 builds on the GAMSLIB corpus infrastructure from Sprint 13 (219 models cataloged, 160 verified as convex/likely_convex) to create a comprehensive JSON database with schema validation and management tools.

### Key Deliverables
1. **gamslib_status.json** - New database with nested pipeline stage tracking
2. **schema.json** - JSON Schema (Draft-07) for validation
3. **db_manager.py** - Database management script with 8 subcommands
4. **Batch verification results** - nlp2mcp parse status for 160 models
5. **Documentation** - Schema specification and workflow guides

### Prep Phase Summary

| Task | Status | Key Finding |
|------|--------|-------------|
| Task 1: Known Unknowns | ✅ Complete | 26 unknowns identified |
| Task 2: Catalog Quality | ✅ Complete | 9.75/10 quality score |
| Task 3: JSON Schema Best Practices | ✅ Complete | Draft-07 recommended |
| Task 4: jsonschema Library | ✅ Complete | 4.25.1, full support |
| Task 5: Schema Design | ✅ Complete | Draft schema validated |
| Task 6: Parse Rate Analysis | ✅ Complete | 13.3% success rate |
| Task 7: db_manager Patterns | ✅ Complete | 8 subcommands designed |
| Task 8: Performance Baselines | ✅ Complete | ~3 min for 160 models |
| Task 9: Sprint 13 Retrospective | ✅ Complete | 4 recommendations mapped |
| Task 10: Detailed Schedule | ✅ Complete | This document |

### Critical Metrics from Prep Phase

| Metric | Value | Implication |
|--------|-------|-------------|
| Parse success rate | 13.3% | Expect ~23 models to parse (not 48+) |
| Average parse time | 0.97 seconds | Batch completes in ~3 minutes |
| Catalog load time | 2.48 ms | No I/O bottleneck |
| Models to process | 160 | verified_convex + likely_convex |
| License-limited | 10 | Skip during batch verification |

---

## 10-Day Schedule

### Phase 1: Schema Finalization (Days 1-2)

#### Day 1: Schema Review and Finalization

**Focus:** Finalize schema.json from draft

| Task | Est. Time | Description |
|------|-----------|-------------|
| Review DRAFT_SCHEMA.json | 1h | Final review of draft schema |
| Update field descriptions | 1h | Ensure all fields are documented |
| Add migration metadata | 0.5h | Add `migrated_from` field |
| Create schema.json | 0.5h | Copy to `data/gamslib/schema.json` |
| Validate schema syntax | 0.5h | Run Draft7Validator.check_schema() |
| Create test entries | 0.5h | Minimal, full, error case entries |

**Deliverables:**
- `data/gamslib/schema.json` (finalized)
- Test entry files for validation

**Acceptance Criteria:**
- [x] Schema passes Draft7Validator.check_schema()
- [x] All 3 test entries validate correctly
- [x] Field descriptions complete

#### Day 2: Migration Script and Database Initialization

**Focus:** Create migration from catalog.json to gamslib_status.json

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create migrate_catalog.py | 2h | Script to transform catalog.json |
| Map catalog fields to new schema | 1h | Field-by-field transformation |
| Handle missing optional fields | 0.5h | Set defaults for new fields |
| Test migration | 1h | Validate all 219 entries migrate |
| Create initial gamslib_status.json | 0.5h | Run migration |
| Verify migration completeness | 0.5h | Compare field counts |

**Deliverables:**
- `scripts/gamslib/migrate_catalog.py`
- `data/gamslib/gamslib_status.json` (v2.0.0)

**Acceptance Criteria:**
- [ ] All 219 models migrated
- [ ] No data loss from catalog.json
- [ ] Database validates against schema.json

---

### Phase 2: db_manager.py Implementation (Days 3-5)

#### Day 3: Core Infrastructure and Basic Subcommands

**Focus:** db_manager.py skeleton with init, validate, list

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create db_manager.py structure | 1h | argparse, logging, main() |
| Implement database loading | 1h | load_database(), save_database() |
| Implement schema validation | 1h | validate subcommand |
| Implement init subcommand | 1h | Initialize from migration or empty |
| Implement list subcommand | 1h | List all models with summary |
| Add backup functionality | 0.5h | Auto-backup before writes |
| Write unit tests | 1h | Test core functions |

**Deliverables:**
- `scripts/gamslib/db_manager.py` (partial)
- Unit tests for core functions

**Acceptance Criteria:**
- [ ] `db_manager.py validate` works
- [ ] `db_manager.py list` shows all 219 models
- [ ] `db_manager.py init` creates valid database
- [ ] Backups created in archive/ directory

**Checkpoint (Day 3):** Schema complete and validated ✓

#### Day 4: CRUD Subcommands

**Focus:** get, update subcommands

| Task | Est. Time | Description |
|------|-----------|-------------|
| Implement get subcommand | 1.5h | Get single model by ID |
| Implement update subcommand | 2h | Update field(s) with validation |
| Handle nested field updates | 1h | e.g., `nlp2mcp_parse.status` |
| Add update validation | 0.5h | Validate after update |
| Write unit tests | 1.5h | Test get/update scenarios |

**Deliverables:**
- get and update subcommands working
- Unit tests for CRUD operations

**Acceptance Criteria:**
- [ ] `db_manager.py get trnsport` returns model details
- [ ] `db_manager.py update trnsport nlp2mcp_parse.status success` works
- [ ] Invalid updates rejected with clear error

#### Day 5: Query and Export Subcommands

**Focus:** query, export, stats subcommands

| Task | Est. Time | Description |
|------|-----------|-------------|
| Implement query subcommand | 2h | Query by field values |
| Add query output formats | 1h | table, json, count |
| Implement export subcommand | 1.5h | CSV, Markdown export |
| Implement stats subcommand | 1h | Database statistics |
| Write unit tests | 1h | Test query/export |
| Integration testing | 0.5h | End-to-end workflow |

**Deliverables:**
- Complete db_manager.py with all 8 subcommands
- Comprehensive unit tests

**Acceptance Criteria:**
- [ ] `db_manager.py query --type LP` returns 57 models
- [ ] `db_manager.py export --format csv` produces valid CSV
- [ ] `db_manager.py stats` shows summary statistics
- [ ] All subcommands have --help documentation

**Checkpoint (Day 5):** db_manager core functions working ✓

---

### Phase 3: Batch Verification Execution (Days 6-7)

#### Day 6: Batch Parse Script

**Focus:** Run nlp2mcp parse on all candidate models

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create batch_parse.py | 2h | Parse all verified/likely_convex models |
| Integrate with db_manager | 1h | Update database with results |
| Add progress reporting | 0.5h | Every 10 models |
| Add error categorization | 1h | 5 error categories from Task 6 |
| Run batch parse | 0.5h | ~3 minutes for 160 models |
| Analyze results | 1h | Generate summary report |

**Deliverables:**
- `scripts/gamslib/batch_parse.py`
- Updated gamslib_status.json with parse results
- Parse summary report

**Acceptance Criteria:**
- [ ] 160 models attempted (skip 10 license-limited)
- [ ] Parse status recorded for each model
- [ ] Error categories assigned
- [ ] ~15-25 models parse successfully (~13% rate; range allows for variance around 13.3% baseline)

#### Day 7: Batch Translate and Results Integration

**Focus:** Run translation on successful parses, consolidate results

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create batch_translate.py | 1.5h | Translate successfully parsed models |
| Run batch translate | 0.5h | Process ~20 models |
| Verify MCP output files | 1h | Check generated .gms files |
| Update database with results | 0.5h | Translate status/errors |
| Generate verification report | 1h | Summary of all stages |
| Review and document results | 1h | Notes on failures |

**Deliverables:**
- `scripts/gamslib/batch_translate.py`
- MCP output files in `data/gamslib/mcp/`
- Verification summary report

**Acceptance Criteria:**
- [ ] All successfully parsed models attempted translation
- [ ] MCP files generated for successful translations
- [ ] Database updated with all pipeline stages
- [ ] Summary report documents all results

**Checkpoint (Day 7):** Verification batch complete ✓

---

### Phase 4: Integration and Testing (Days 8-9)

#### Day 8: Integration Testing and Edge Cases

**Focus:** Test full workflow, handle edge cases

| Task | Est. Time | Description |
|------|-----------|-------------|
| End-to-end workflow test | 1.5h | init → parse → translate → query |
| Test error recovery | 1h | Backup/restore, invalid updates |
| Test concurrent access | 0.5h | Multiple read operations |
| Fix any discovered issues | 2h | Buffer for bug fixes |
| Update tests for edge cases | 1h | Add missing test coverage |

**Deliverables:**
- All edge cases handled
- Bug fixes implemented
- Test coverage complete

**Acceptance Criteria:**
- [ ] Full workflow completes without errors
- [ ] Error recovery works correctly
- [ ] All tests pass
- [ ] No critical bugs remaining

#### Day 9: Documentation and Schema Documentation

**Focus:** Complete all documentation

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create GAMSLIB_DATABASE_SCHEMA.md | 2h | Schema specification document |
| Document db_manager usage | 1h | All subcommands with examples |
| Update existing docs | 1h | References to new database |
| Create workflow guide | 1h | How to use the system |
| Review and polish | 0.5h | Final documentation review |

**Deliverables:**
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md`
- db_manager.py has complete --help for all subcommands
- Workflow guide for batch operations

**Acceptance Criteria:**
- [ ] Schema fully documented
- [ ] All fields described with valid values
- [ ] Usage examples for all subcommands
- [ ] Workflow guide complete

---

### Phase 5: Review and Finalization (Day 10)

#### Day 10: Final Review and Sprint Completion

**Focus:** Final validation, cleanup, and sprint closure

| Task | Est. Time | Description |
|------|-----------|-------------|
| Final database validation | 0.5h | Validate all entries |
| Final test run | 1h | All tests pass |
| Code review and cleanup | 1h | Remove debug code, format |
| Update CHANGELOG.md | 0.5h | Document all changes |
| Create SPRINT_SUMMARY.md | 1h | Sprint results documentation |
| Final acceptance check | 0.5h | Verify all criteria met |
| Merge to main | 0.5h | PR review and merge |

**Deliverables:**
- All deliverables complete and validated
- SPRINT_SUMMARY.md
- Updated CHANGELOG.md
- Merged to main branch

**Acceptance Criteria:**
- [ ] All acceptance criteria from PROJECT_PLAN.md met
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code merged to main

**Checkpoint (Day 10):** All deliverables ready ✓

---

## Checkpoints Summary

| Day | Checkpoint | Success Criteria |
|-----|------------|------------------|
| 3 | Schema complete | schema.json validated, migration complete |
| 5 | db_manager working | All 8 subcommands functional, tests passing |
| 7 | Verification complete | 160 models processed, results in database |
| 10 | Sprint complete | All deliverables ready, merged to main |

---

## Risks and Mitigations

### Risk 1: Schema Design Changes Mid-Sprint

**Likelihood:** Low  
**Impact:** Medium (2-4 hours rework)

**Mitigation:**
- Draft schema validated in prep phase (Task 5)
- Schema review on Day 1 before implementation
- Use schema versioning for any changes

### Risk 2: Parse Rate Lower Than Expected

**Likelihood:** Low (already measured at 13.3%)  
**Impact:** Low (fewer models to track, but system still works)

**Mitigation:**
- Accept that ~15-25 models will parse successfully
- Focus on tracking all models regardless of parse status
- Document parse failures for future parser improvements

### Risk 3: db_manager Implementation Delays

**Likelihood:** Medium  
**Impact:** Medium (could delay batch verification)

**Mitigation:**
- Follow existing script patterns (Task 7)
- Start with minimal viable subcommands
- Query and export can be simplified if needed
- Days 4-5 have buffer time

### Risk 4: Integration Issues Between Components

**Likelihood:** Low  
**Impact:** Medium (debugging time)

**Mitigation:**
- Use consistent patterns from existing scripts
- Test integration incrementally
- Day 8 dedicated to integration testing
- 2-hour buffer for bug fixes

### Risk 5: jsonschema Library Issues

**Likelihood:** Very Low (tested in Task 4)  
**Impact:** High (schema validation won't work)

**Mitigation:**
- Library version 4.25.1 confirmed working
- Validation patterns tested in prep phase
- Fallback: manual validation if library fails

---

## Resource Requirements

### Development Environment
- Python 3.12+ with virtual environment
- jsonschema 4.25.1 (already installed)
- pytest for testing
- Git for version control

### Files to Create
- `data/gamslib/schema.json`
- `data/gamslib/gamslib_status.json`
- `data/gamslib/archive/` (directory)
- `scripts/gamslib/migrate_catalog.py`
- `scripts/gamslib/db_manager.py`
- `scripts/gamslib/batch_parse.py`
- `scripts/gamslib/batch_translate.py`
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md`

### Files to Update
- `CHANGELOG.md`
- `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`

---

## Acceptance Criteria (from PROJECT_PLAN.md)

### Convexity Verification
- [x] 160 candidate models identified (from Sprint 13)
- [ ] All 160 models processed through nlp2mcp parse
- [ ] Parse/translate results recorded in database
- [ ] ~15-25 models successfully parsed (adjusted from original 30+ target)

### Database Schema
- [ ] Complete schema documented with all fields specified
- [ ] Schema validates all entries correctly
- [ ] Nested structure for pipeline stages implemented
- [ ] Error categories captured in structured format

### Database Manager
- [ ] All 8 subcommands functional (init, get, update, query, validate, list, export, stats)
- [ ] Schema validation catches invalid entries
- [ ] Atomic updates with backup strategy
- [ ] Export to CSV and Markdown working

### Documentation
- [ ] Schema and workflow fully documented
- [ ] db_manager usage examples provided
- [ ] Migration from catalog.json documented

### Quality
- [ ] Database manager has comprehensive tests
- [ ] All tests passing
- [ ] Code follows existing project patterns

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Models in database | 219 | Count from gamslib_status.json |
| Parse attempts | 160 | Models with nlp2mcp_parse status |
| Parse success | 15-25 | Models with status "success" |
| Translate attempts | All successful parses | Models with nlp2mcp_translate status |
| db_manager subcommands | 8 | Working subcommands |
| Test coverage | >80% | pytest coverage report |
| Documentation pages | 3+ | New documentation files |

---

## Daily Standup Format

Each day, track:
1. **Completed:** Tasks finished yesterday
2. **Planned:** Tasks for today
3. **Blockers:** Any issues preventing progress
4. **Unknowns:** New discoveries to document

Update `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md` daily.

---

## Appendix A: Verified Unknowns Summary

### Category 1: Complete Convexity Verification (5 unknowns)

| Unknown | Status | Decision |
|---------|--------|----------|
| 1.1 Batch verification timing | ✅ Verified | ~3 minutes for 160 models |
| 1.2 Parse success rate | ✅ Verified | 13.3% (not 30% assumed) |
| 1.3 License limit handling | ✅ Verified | Mark as license_limited, skip 10 models |
| 1.4 Missing $include files | ✅ Verified | Only 2 models affected |
| 1.5 Update target file | ✅ Verified | New gamslib_status.json, not catalog.json |

### Category 2: JSON Database Schema Design (7 unknowns)

| Unknown | Status | Decision |
|---------|--------|----------|
| 2.1 Schema draft version | ✅ Verified | Draft-07 |
| 2.2 Nested vs flat structure | ✅ Verified | Moderate nesting (2 levels) |
| 2.3 Required vs optional fields | ✅ Verified | Core fields required, stages optional |
| 2.4 Pipeline status enums | ✅ Verified | Stage-specific enums defined |
| 2.5 Error message storage | ✅ Verified | Structured error objects |
| 2.6 Version tracking | ✅ Verified | nlp2mcp_version per stage |
| 2.7 Schema migrations | ✅ Verified | Semantic versioning, eager migration |

### Category 3: Database Management Scripts (6 unknowns)

| Unknown | Status | Decision |
|---------|--------|----------|
| 3.1 Essential subcommands | ✅ Verified | 8 subcommands defined |
| 3.2 Concurrent access | 🔍 Deferred | Sequential access sufficient for Sprint 14 |
| 3.3 Query interface | 🔍 Deferred | Simple key-value filtering |
| 3.4 Export formats | 🔍 Deferred | CSV and Markdown |
| 3.5 Script patterns | ✅ Verified | Follow existing patterns |
| 3.6 Backup strategy | ✅ Verified | Auto-backup in archive/, keep 10 |

### Category 4: Version Control Strategy (4 unknowns)

| Unknown | Status | Decision |
|---------|--------|----------|
| 4.1 Version control database | 🔍 Deferred | Yes, git-tracked |
| 4.2 PR handling | 🔍 Deferred | Commit with code changes |
| 4.3 Schema file separation | ✅ Verified | Separate schema.json file |
| 4.4 Archive strategy | 🔍 Deferred | Timestamped in archive/ |

### Category 5: Multi-Solver Validation (4 unknowns)

| Unknown | Status | Decision |
|---------|--------|----------|
| 5.1 Secondary solvers | 🔍 Deferred | Optional feature |
| 5.2 Solution matching | 🔍 Deferred | Tolerance-based comparison |
| 5.3 Sequential vs parallel | ✅ Verified | Sequential recommended |
| 5.4 Disagreement handling | 🔍 Deferred | Flag for review |

**Total Verified:** 17/26 (65%)  
**Deferred to Implementation:** 9/26 (35%)

---

## Appendix B: File Structure After Sprint 14

```
data/gamslib/
├── catalog.json              # Sprint 13 archive (read-only)
├── gamslib_status.json       # Sprint 14 database (v2.0.0)
├── schema.json               # JSON Schema definition (Draft-07)
├── archive/                  # Timestamped backups
│   └── YYYYMMDD_HHMMSS_gamslib_status.json
├── raw/                      # Original GAMSLIB model files
│   └── *.gms
└── mcp/                      # Generated MCP files
    └── *_mcp.gms

scripts/gamslib/
├── catalog.py                # Dataclass definitions
├── discover_models.py        # Model discovery
├── download_models.py        # Model download
├── verify_convexity.py       # Convexity verification
├── migrate_catalog.py        # NEW: Migration script
├── db_manager.py             # NEW: Database management
├── batch_parse.py            # NEW: Batch parse script
└── batch_translate.py        # NEW: Batch translate script

docs/
├── infrastructure/
│   └── GAMSLIB_DATABASE_SCHEMA.md  # NEW: Schema documentation
└── planning/EPIC_3/SPRINT_14/
    ├── PLAN.md               # This document
    ├── SPRINT_LOG.md         # Daily progress
    ├── SPRINT_SUMMARY.md     # Final summary
    ├── KNOWN_UNKNOWNS.md     # Verified unknowns
    ├── DRAFT_SCHEMA.json     # Draft schema (from prep)
    └── SCHEMA_DESIGN_NOTES.md # Design rationale
```

---

## Appendix C: Quick Reference Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run schema validation
python scripts/gamslib/db_manager.py validate

# List all models
python scripts/gamslib/db_manager.py list

# Get single model
python scripts/gamslib/db_manager.py get trnsport

# Update model field
python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success

# Query by type
python scripts/gamslib/db_manager.py query --type LP

# Export to CSV
python scripts/gamslib/db_manager.py export --format csv > models.csv

# Show statistics
python scripts/gamslib/db_manager.py stats

# Run tests
pytest tests/gamslib/ -v

# Run batch parse
python scripts/gamslib/batch_parse.py --all

# Run batch translate
python scripts/gamslib/batch_translate.py --parsed-only
```

---

*Document created: January 1, 2026*  
*Last updated: January 1, 2026*  
*Sprint 14 Prep Task 10*
