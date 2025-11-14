# GAMSLib Ingestion Schedule and Automation Strategy

**Date:** 2025-11-13  
**Issue:** 3.6 (Low Priority)  
**Owner:** GAMSLib Team  
**Status:** ✅ RESOLVED - Sprint 6 Decision

---

## Assumption

GAMSLib model ingestion needs a defined cadence and level of automation. The decision impacts Sprint 6 scope and future automation work.

---

## Research Questions

1. Should ingestion be manual, semi-automated, or fully automated?
2. What is the appropriate cadence: ad-hoc, weekly, sprint-based?
3. What infrastructure is needed for automated ingestion?
4. When should automation be implemented?
5. What are the prerequisites for a `make ingest-gamslib` target?

---

## Investigation

### Ingestion Process Overview

The GAMSLib ingestion process consists of:

```
1. Download Models (scripts/download_gamslib_nlp.sh)
   ↓
2. Run Ingestion (scripts/ingest_gamslib.py)
   ↓
3. Generate Reports (reports/gamslib_ingestion_sprint6.json)
   ↓
4. Update Documentation (docs/research/gamslib_parse_errors.md)
```

### Automation Options Analysis

#### Option A: Fully Manual (Current)
**Process:**
- Developer manually runs download script
- Developer manually runs ingestion script
- Developer manually reviews results
- Developer manually updates documentation

**Pros:**
- Simplest to implement for Sprint 6
- Full developer control over validation
- No infrastructure required

**Cons:**
- Time-consuming for future sprints
- Prone to human error
- Not scalable to larger model sets

#### Option B: Semi-Automated (make target)
**Process:**
- Single `make ingest-gamslib` command runs entire pipeline
- Automated: download, ingest, generate reports
- Manual: review results, update docs, commit changes

**Pros:**
- One-command operation
- Consistent execution
- Reduces manual errors

**Cons:**
- Requires makefile integration
- Still needs manual review/commit
- Development effort needed

#### Option C: Fully Automated (CI/CD)
**Process:**
- Scheduled GitHub Actions workflow
- Automated: download, ingest, commit results
- Notifications on parse rate changes

**Pros:**
- No manual intervention
- Regular cadence (e.g., weekly)
- Continuous monitoring

**Cons:**
- Significant infrastructure work
- Requires CI/CD setup
- May generate noisy commits
- Overkill for Sprint 6 scope

---

## Decision: Manual Ingestion for Sprint 6

### Rationale

**For Sprint 6 (10 models, baseline establishment):**
- Manual ingestion is sufficient for initial validation
- Allows careful review of parse errors
- Focuses development effort on core parser improvements
- Avoids premature optimization

**Deferral to Sprint 7+:**
- After baseline is established, automation value increases
- Parser stability will improve (fewer surprises)
- Larger model sets will justify automation investment

### Sprint 6 Approach

1. **Download** (already complete): `scripts/download_gamslib_nlp.sh`
2. **Ingest**: Run `python scripts/ingest_gamslib.py` manually
3. **Review**: Examine `reports/gamslib_ingestion_sprint6.json`
4. **Document**: Update `docs/research/gamslib_parse_errors.md`
5. **Commit**: Manually commit results to repository

**Cadence:** Once per sprint (Sprint 6 initial run only)

---

## Prerequisites for `make ingest-gamslib` Target (Future)

When automation is implemented in Sprint 7+, the makefile target should:

### Requirements

1. **Dependencies Check**
   ```bash
   # Verify Python environment
   # Verify test fixtures directory exists
   # Verify scripts/ingest_gamslib.py exists
   ```

2. **Execution Steps**
   ```bash
   # 1. Download models (if not already present)
   ./scripts/download_gamslib_nlp.sh
   
   # 2. Run ingestion
   python scripts/ingest_gamslib.py \
       --input tests/fixtures/gamslib \
       --output reports/gamslib_ingestion.json
   
   # 3. Display summary
   python scripts/summarize_ingestion.py reports/gamslib_ingestion.json
   ```

3. **Output Verification**
   - Check that `reports/gamslib_ingestion.json` was created
   - Verify JSON format is valid
   - Display parse%, convert%, solve% metrics

4. **Error Handling**
   - Exit with error if ingestion script fails
   - Provide clear error messages
   - Preserve partial results for debugging

### Example Makefile Target (Future)

```makefile
.PHONY: ingest-gamslib
ingest-gamslib: ## Run GAMSLib model ingestion pipeline
	@echo "Starting GAMSLib ingestion..."
	@./scripts/download_gamslib_nlp.sh
	@python scripts/ingest_gamslib.py \
		--input tests/fixtures/gamslib \
		--output reports/gamslib_ingestion.json
	@python scripts/summarize_ingestion.py reports/gamslib_ingestion.json
	@echo "✅ Ingestion complete. Report: reports/gamslib_ingestion.json"
```

---

## Future Automation Roadmap

### Sprint 7+: Semi-Automation
- Implement `make ingest-gamslib` target
- Add ingestion summary script
- Document in developer workflow

### Sprint 8+: CI Integration (Optional)
- Add GitHub Actions workflow
- Schedule weekly/monthly runs
- Automated PR creation with results
- Metrics tracking dashboard

---

## Sprint 6 Acceptance Criteria

- ✅ Ingestion schedule decision documented
- ✅ Manual approach defined for Sprint 6
- ✅ Automation prerequisites identified
- ✅ Future roadmap established
- ✅ 10 models successfully ingested using manual process

---

## References

- **Day 0 Research:** Unknown 3.3 (Parse Errors), Unknown 3.5 (KPI Definitions)
- **Task 7:** `scripts/download_gamslib_nlp.sh` implementation
- **Day 5 Plan:** Sprint 6 PLAN.md lines 276-323
