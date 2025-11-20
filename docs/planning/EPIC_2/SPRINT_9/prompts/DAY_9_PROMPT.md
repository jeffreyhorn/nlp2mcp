# Day 9 Prompt: Dashboard & Performance Instrumentation

**Branch:** Create a new branch named `sprint9-day9-dashboard-performance` from `sprint9-advanced-features`

**Objective:** Add essential Sprint 9 metrics to dashboard (parse rate, conversion count) and implement CI performance budget enforcement (minimal).

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 984-1036) - Day 9 summary
- Verify Checkpoint 4 passed: 1 model converts, validation working
- Review current dashboard: `scripts/dashboard.py`
- Review performance budget framework from Task 9

**Tasks to Complete (1.5 hours):**

1. **Add parse rate to dashboard (with i++1/model sections breakdown)** (45 minutes)
   - Open `scripts/dashboard.py`
   - Add parse rate metrics with feature breakdown:
     ```python
     def generate_parse_rate_summary() -> dict:
         """Generate parse rate summary with feature breakdown."""
         total_models = 10  # GAMSLib subset
         passing_models = count_passing_models()
         
         # Feature-specific unlocks
         unlocked_by_i_plusplus_1 = ["himmel16"]
         unlocked_by_model_sections = ["hs62"]
         unlocked_by_attributes = ["mingamma"] if mingamma_parses() else []
         
         return {
             "total_models": total_models,
             "passing_models": passing_models,
             "parse_rate_percent": (passing_models / total_models) * 100,
             "baseline_models": ["mhw4d", "rbrock", "mathopt1", "trig"],
             "unlocked_by_features": {
                 "i++1_indexing": unlocked_by_i_plusplus_1,
                 "model_sections": unlocked_by_model_sections,
                 "equation_attributes": unlocked_by_attributes
             }
         }
     ```
   - Add to dashboard output:
     ```
     ## Sprint 9 Parse Rate
     
     **Overall:** XX% (X/10 models)
     
     **Baseline models (Sprint 8):**
     - mhw4d ✅
     - rbrock ✅
     - mathopt1 ✅
     - trig ✅
     
     **Sprint 9 unlocks:**
     - himmel16 ✅ (i++1 indexing)
     - hs62 ✅ (model sections)
     - mingamma [✅/❌] (equation attributes)
     ```
   - Regenerate dashboard: `python scripts/dashboard.py`

2. **Add conversion success count to dashboard** (30 minutes)
   - Add conversion metrics to dashboard:
     ```python
     def generate_conversion_summary() -> dict:
         """Generate conversion pipeline summary."""
         converted_models = find_converted_models("output/")
         
         return {
             "models_converted": len(converted_models),
             "conversion_rate_percent": (len(converted_models) / passing_models) * 100,
             "converted_list": converted_models,
             "conversion_gaps": load_conversion_gaps()  # From docs/conversion/gaps.md
         }
     ```
   - Add to dashboard:
     ```
     ## Conversion Pipeline
     
     **Converted:** X/Y models (XX% of parseable models)
     
     **Successfully converted:**
     - [model name] ✅
     
     **Known gaps:** [Link to docs/conversion/gaps.md]
     ```

3. **Implement CI performance budget check (fail if >30s)** (15 minutes)
   - Create or update `.github/workflows/performance-check.yml`:
     ```yaml
     name: Performance Budget Check
     
     on: [pull_request]
     
     jobs:
       check-performance:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3
           
           - name: Setup Python
             uses: actions/setup-python@v4
             with:
               python-version: '3.11'
           
           - name: Install dependencies
             run: pip install -r requirements.txt
           
           - name: Run fast tests with timing
             run: |
               start_time=$(date +%s)
               pytest -m "not slow" --tb=short
               end_time=$(date +%s)
               duration=$((end_time - start_time))
               echo "Fast test duration: ${duration}s"
               
               # Check budget
               if [ $duration -gt 30 ]; then
                 echo "❌ BUDGET EXCEEDED: Fast tests took ${duration}s (budget: 30s)"
                 exit 1
               else
                 echo "✅ Within budget: ${duration}s / 30s"
               fi
     ```
   - Minimal implementation (no detailed metrics, just pass/fail)
   - Budget: Fail if >30s, warn if >27s

**Deliverables:**
- Updated `scripts/dashboard.py` with parse rate + conversion metrics
- Updated `.github/workflows/performance-check.yml` with basic budget check
- Regenerated dashboard showing Sprint 9 achievements

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass (fast tests <30s)

**Completion Criteria:**
- [ ] Dashboard shows updated parse rate (≥50%)
- [ ] Dashboard shows conversion count (≥1 model)
- [ ] CI fails if fast tests >30s
- [ ] All quality checks pass
- [ ] Mark Day 9 complete in PLAN.md
- [ ] Update README.md and CHANGELOG.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 9 Day 9: Dashboard & Performance Instrumentation" \
             --body "Completes Day 9 tasks from Sprint 9 PLAN.md

## Dashboard Updates
- Parse rate with feature breakdown: XX%
- Conversion success count: X models
- Feature-specific unlocks documented

## CI Performance Budget
- Budget enforcement: Fail if >30s
- Current fast test duration: XX.XXs
- Status: [WITHIN/OVER] budget

## Sprint 9 Metrics Summary
- Parse rate: XX% (X/10 models)
- Models unlocked: himmel16 (i++1), hs62 (model sections), [mingamma]
- Conversion: X models converted successfully

Ready for Day 10 (closeout and documentation)." \
             --base sprint9-advanced-features
```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 984-1036)
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 9)
- `docs/performance/baselines/budgets.json`

**Notes:**
- Effort: 1.5h total (descoped from original 2.5-3h)
- Focus on essential metrics only (parse rate + conversion)
- Minimal CI integration (basic budget check only)
- Detailed dashboard metrics deferred to Sprint 10
- Day 9 is streamlined to stay within budget
