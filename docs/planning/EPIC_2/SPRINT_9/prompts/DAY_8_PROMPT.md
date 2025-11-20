# Day 8 Prompt: Conversion Pipeline - Part 2 → CHECKPOINT 4

**Branch:** Create a new branch named `sprint9-day8-conversion-pipeline-part2-checkpoint4` from `sprint9-advanced-features`

**Objective:** Convert at least 1 model end-to-end (GAMS NLP → MCP GAMS), validate MCP GAMS output parses successfully, implement conversion validation script, and achieve Checkpoint 4 (1 model converts).

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 888-938) - Day 8 summary
- Verify Day 7 complete: Converter infrastructure working, all mappings implemented
- Review mhw4d.gms and rbrock.gms as conversion candidates
- Verify unit tests pass for converter

**Tasks to Complete (2-3 hours):**

1. **Convert mhw4d.gms or rbrock.gms end-to-end** (1 hour)
   - Choose simpler model (likely mhw4d.gms based on Task 5 analysis)
   - Run full pipeline:
     ```python
     # Parse GAMS source → IR
     ir = parse_file("data/gamslib/mhw4d.gms")
     
     # Convert IR → MCP GAMS
     converter = Converter(ir)
     result = converter.convert()
     
     # Save MCP GAMS output
     with open("output/mhw4d_mcp.gms", "w") as f:
         f.write(result.output)
     ```
   - Expected output: Valid GAMS file in MCP format
   - Document any missing mappings or unsupported IR nodes

2. **Debug conversion failures (if any)** (0.5-1 hour)
   - If conversion fails:
     - Check error messages (which IR node failed?)
     - Identify missing mappings
     - Options:
       - Add missing mappings (if simple)
       - Document unsupported features (if complex)
       - Try rbrock.gms if mhw4d too complex
   - Common issues:
     - Unsupported expression types
     - Missing set declarations
     - Complex indexing patterns
   - Recovery from PLAN.md (lines 888-938):
     - Accept "partial conversion" as deliverable
     - Document gaps for Sprint 10

3. **Implement conversion validation script** (1 hour)
   - Create `scripts/validate_conversion.py`
   - Validation checks:
     ```python
     def validate_conversion(mcp_gams_file: Path) -> ValidationResult:
         """Validate MCP GAMS output."""
         checks = []
         
         # Check 1: File is valid GAMS syntax
         checks.append(check_gams_syntax(mcp_gams_file))
         
         # Check 2: All variables declared
         checks.append(check_variables_declared(mcp_gams_file))
         
         # Check 3: All parameters declared
         checks.append(check_parameters_declared(mcp_gams_file))
         
         # Check 4: All equations declared
         checks.append(check_equations_declared(mcp_gams_file))
         
         # Check 5: No undefined references
         checks.append(check_no_undefined_refs(mcp_gams_file))
         
         return ValidationResult(
             success=all(c.passed for c in checks),
             checks=checks
         )
     
     def check_gams_syntax(file: Path) -> CheckResult:
         """Verify GAMS syntax is valid."""
         try:
             # Use GAMS parser or linter
             result = subprocess.run(
                 ["gams", str(file), "check"],
                 capture_output=True,
                 timeout=30
             )
             return CheckResult(
                 name="GAMS syntax",
                 passed=(result.returncode == 0),
                 message=result.stderr.decode() if result.returncode != 0 else "Valid"
             )
         except Exception as e:
             return CheckResult(
                 name="GAMS syntax",
                 passed=False,
                 message=f"Error checking syntax: {e}"
             )
     ```
   - Note: If GAMS not available, implement text-based validation
   - Exit code 0 if all checks pass, 1 if any fail

4. **Validate MCP GAMS output parses as valid GAMS** (30 minutes)
   - Run validation script on converted file:
     ```bash
     python scripts/validate_conversion.py output/mhw4d_mcp.gms
     ```
   - Expected: All validation checks pass
   - If validation fails:
     - Fix syntax errors in converter
     - Document known limitations
   - **Acceptance criterion:** At least 1 model converts to valid MCP GAMS
   - If both mhw4d and rbrock fail:
     - Document blockers
     - Consider "partial conversion" as Sprint 9 deliverable

**Deliverables:**
- mhw4d.gms or rbrock.gms converted to MCP GAMS format (in `output/` directory)
- `scripts/validate_conversion.py` - Conversion validation script
- MCP GAMS output validated (passes syntax checks)
- Documentation of conversion gaps (if any) in `docs/conversion/gaps.md`

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] At least 1 model converts successfully (mhw4d or rbrock)
  - [ ] MCP GAMS output parses successfully as valid GAMS
  - [ ] Conversion validation script working
  - [ ] All quality checks pass
  - [ ] **CHECKPOINT 4 PASSED** (see below)
- [ ] Mark Day 8 complete in PLAN.md
- [ ] Update README.md and CHANGELOG.md
- [ ] **Check off all Checkpoint 4 criteria in PLAN.md**

**Checkpoint 4 Criteria (PLAN.md lines 940-982):**
- [ ] Converter class scaffolding complete (Day 7)
- [ ] IR → MCP GAMS mappings for variables, parameters, equations (Day 7)
- [ ] At least 1 model converts successfully (mhw4d or rbrock)
- [ ] MCP GAMS output parses successfully as valid GAMS
- [ ] Conversion validation script working

**Checkpoint 4 Decision:**
- **GO:** All 5 criteria met → Proceed to Day 9 (dashboard + performance)
- **NO-GO:** Conversion fails → Spend Day 9 debugging, use Day 10 buffer, document partial conversion

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 9 Day 8: Conversion Pipeline - Part 2 → CHECKPOINT 4" \
             --body "Completes Day 8 tasks and achieves Checkpoint 4

## End-to-End Conversion ✅
- Model converted: [mhw4d/rbrock]
- Conversion status: [SUCCESS/PARTIAL]
- MCP GAMS output: output/[model]_mcp.gms

## Validation
- GAMS syntax: [PASS/FAIL]
- All declarations present: [PASS/FAIL]
- No undefined references: [PASS/FAIL]

## Checkpoint 4 Status: [PASS/NO-GO]
- [x] Converter scaffolding complete
- [x] IR → MCP mappings complete
- [x] 1 model converts
- [x] MCP GAMS validates
- [x] Validation script working

## Known Gaps
[List any documented conversion limitations]

Ready for Day 9 (dashboard and performance instrumentation)." \
             --base sprint9-advanced-features
```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 888-982)
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 5)
- `data/gamslib/mhw4d.gms` or `data/gamslib/rbrock.gms`

**Notes:**
- Effort: 2-3h (1h conversion + 0.5-1h debug + 1h validation + 0.5h testing)
- Checkpoint 4 is final technical checkpoint
- Conversion is Sprint 9 stretch goal (acceptable to have gaps)
- Document all conversion limitations for Sprint 10
- If validation requires GAMS compiler and not available, use text-based checks
