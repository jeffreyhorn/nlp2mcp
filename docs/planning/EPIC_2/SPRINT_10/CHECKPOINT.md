# Sprint 10 Mid-Sprint Checkpoint Guide

## Overview

This document explains how to use the Sprint 10 mid-sprint checkpoint infrastructure to validate progress and make informed decisions at the Day 5 milestone.

## Purpose

The checkpoint system addresses a critical lesson from Sprint 9:

**Sprint 9 Lesson:**
- All 3 features completed by Day 5
- Parse rate improvement: 0% (discovered only on Day 10)
- Too late to pivot or adjust strategy
- Result: Sprint goal partially achieved (10% improvement instead of 20%)

**Sprint 10 Solution:**
- Day 5 checkpoint validates parse rate progress
- Early detection of issues enables mid-sprint corrections
- Enables informed decision-making about sprint strategy

## When to Run

**Recommended schedule:**
- **Day 5 of Sprint 10** (mid-sprint checkpoint)
- After implementing 2-3 planned features
- Before committing to remaining features

**Optional additional checkpoints:**
- Day 3 (early warning)
- Day 7 (post-checkpoint progress check)
- Day 9 (final validation before sprint end)

## How to Run

### Quick Check

```bash
./scripts/sprint10_checkpoint.sh
```

This runs the full checkpoint validation and provides a status report.

### Detailed Parse Rate Measurement

```bash
python scripts/measure_parse_rate.py --verbose
```

This shows detailed results for each model:
```
Testing GAMSLIB Tier 1 models...
============================================================
✅ PASS  circle.gms
❌ FAIL  himmel16.gms
✅ PASS  hs62.gms
✅ PASS  mathopt1.gms
❌ FAIL  maxmin.gms
✅ PASS  mhw4d.gms
✅ PASS  mhw4dx.gms
❌ FAIL  mingamma.gms
✅ PASS  rbrock.gms
✅ PASS  trig.gms
============================================================
Parse Rate: 7/10 models (70.0%)

Failed models:
  - himmel16.gms
  - maxmin.gms
  - mingamma.gms
```

## Interpreting Results

### Scenario 1: On Track (✅)

**Indicators:**
- Current parse rate ≥ 70% (7/10 models)
- Meeting or exceeding Day 5 projection
- Green status message from checkpoint script

**What it means:**
- Sprint 10 implementation is progressing as planned
- Current features are working correctly
- Trajectory suggests sprint goal (90%) is achievable

**Next steps:**
1. Continue implementing remaining planned features
2. Stay on current schedule and trajectory
3. Monitor for any regressions
4. Consider stretch goals if ahead of schedule

**Example output:**
```
✅ STATUS: ON TRACK

Parse rate meets or exceeds Day 5 minimum target.

Next steps:
  - Continue implementing planned features
  - 2 more model(s) needed to reach sprint goal
  - Stay on current trajectory
```

### Scenario 2: Behind Schedule (⚠️)

**Indicators:**
- Current parse rate < 70% (fewer than 7/10 models)
- Below Day 5 projection
- Red warning message from checkpoint script

**What it means:**
- Sprint 10 implementation is not progressing as expected
- Current features may have bugs or unexpected complexity
- Risk: Sprint goal (90%) may not be achievable without changes

**Root cause analysis required:**

1. **Review which models are failing:**
   ```bash
   python scripts/measure_parse_rate.py --verbose
   ```
   
2. **Check if failures match expectations:**
   - Are models failing that should be passing?
   - Are implemented features working correctly?
   - Are there unexpected blockers?

3. **Assess implementation quality:**
   - Run test suite: `make test`
   - Check for regressions in previously passing models
   - Verify feature implementations against specifications

4. **Estimate remaining work:**
   - How many features remain to implement?
   - How complex are remaining blockers?
   - Can sprint goal still be achieved in 5 days?

### Action Options (Behind Schedule)

The checkpoint script provides 3 strategic options:

#### Option A: Debug and Fix Current Features

**When to choose:**
- Failures are due to bugs in already-implemented features
- Bugs appear fixable within 1-2 days
- Original sprint plan is still sound

**Steps:**
1. Identify specific bugs causing failures
2. Estimate fix complexity and time
3. Fix bugs and re-run checkpoint
4. Resume original sprint plan if back on track

**Example:**
```
Day 5: 60% parse rate (6/10 models) - behind schedule
Root cause: Bug in comma-separated declarations
Fix estimate: 4 hours
Day 6: 70% parse rate (7/10 models) - back on track
Continue with original plan
```

#### Option B: Pivot to Different Models

**When to choose:**
- Current blockers are more complex than estimated
- Other models have simpler, more achievable blockers
- Can reach 90% goal by targeting different models

**Steps:**
1. Re-analyze remaining failed models
2. Identify models with simpler blockers
3. Estimate effort for alternative targets
4. Update sprint plan to focus on easier wins
5. Document pivot decision and rationale

**Example:**
```
Day 5: 60% parse rate (6/10 models) - behind schedule
Original targets: himmel16.gms (complex), mingamma.gms (complex)
Pivot: Target circle.gms (simpler) instead
New plan: Focus on circle.gms + 2 other simpler models
Expected outcome: 90% achievable with adjusted targets
```

#### Option C: Reduce Scope

**When to choose:**
- Remaining time is insufficient for full sprint goal
- Both original and alternative targets are too complex
- Better to achieve partial success than overcommit

**Steps:**
1. Calculate realistic achievable parse rate
2. Identify highest-value models to target
3. Defer lower-priority models to Sprint 11
4. Update sprint goal and document decision
5. Focus on quality over quantity

**Example:**
```
Day 5: 60% parse rate (6/10 models) - behind schedule
Realistic estimate: 70-80% achievable in remaining 5 days
Decision: Reduce sprint goal from 90% to 80%
Defer: maxmin.gms, himmel16.gms to Sprint 11
Focus: Target circle.gms, mingamma.gms for 80% goal
```

## Decision Framework

Use this framework to decide which option to pursue:

### Step 1: Assess Current State

```bash
python scripts/measure_parse_rate.py --verbose
```

**Questions:**
- How many models are currently passing?
- How far from Day 5 target (70%)?
- Which specific models are failing?

### Step 2: Analyze Failures

For each failed model:
1. Review blocker analysis from prep phase
2. Check if implemented features should unblock it
3. Test features in isolation (synthetic tests)
4. Identify bugs vs. missing features

### Step 3: Estimate Remaining Work

**For each remaining failed model:**
- List required features/fixes
- Estimate implementation time (optimistic/pessimistic)
- Calculate total remaining effort
- Compare to remaining sprint days (5 days from checkpoint)

**Example estimation table:**

| Model | Status | Blocker | Estimate | Priority |
|-------|--------|---------|----------|----------|
| circle.gms | ❌ | Nested indexing | 2-3h | High |
| himmel16.gms | ❌ | Variable bounds + i++1 bug | 4-6h | Medium |
| mingamma.gms | ❌ | Comma-separated scalars | 3-4h | High |
| maxmin.gms | ❌ | Complex function calls | 8-10h | Low (defer) |

**Total remaining:** 17-23 hours (high estimate) vs. 40 hours available (5 days × 8 hours)

### Step 4: Choose Strategy

**Choose Option A (Debug & Fix) if:**
- ✅ Failures are due to fixable bugs
- ✅ Fix estimate < 25% remaining time
- ✅ Original plan viable after fixes

**Choose Option B (Pivot) if:**
- ✅ Alternative targets are significantly simpler
- ✅ Can still achieve 90% goal with pivot
- ✅ Pivot requires < 50% replanning effort

**Choose Option C (Reduce Scope) if:**
- ✅ Remaining work > available time
- ✅ No simpler alternative targets exist
- ✅ Partial success (70-80%) is valuable

**If uncertain:** Spend 2-4 hours on deeper analysis before deciding.

### Step 5: Document Decision

Update sprint documentation:
1. `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md` - Record checkpoint results
2. `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Update targets if pivoting
3. Sprint retrospective - Note decision and rationale

## Example Checkpoint Session

### Scenario: Day 5, Behind Schedule

```bash
$ ./scripts/sprint10_checkpoint.sh

==========================================
Sprint 10 Day 5 Checkpoint
==========================================

Baseline (Day 0): 6/10 models (60%)
Day 5 Target:     7/10 models (70%)
Sprint Goal:      9/10 models (90%)

Measuring current parse rate...

Testing GAMSLIB Tier 1 models...
============================================================
❌ FAIL  circle.gms
❌ FAIL  himmel16.gms
✅ PASS  hs62.gms
✅ PASS  mathopt1.gms
❌ FAIL  maxmin.gms
✅ PASS  mhw4d.gms
✅ PASS  mhw4dx.gms
❌ FAIL  mingamma.gms
✅ PASS  rbrock.gms
✅ PASS  trig.gms
============================================================
Parse Rate: 6/10 models (60.0%)

Failed models:
  - circle.gms
  - himmel16.gms
  - maxmin.gms
  - mingamma.gms

==========================================
Checkpoint Results
==========================================

Current parse rate: 6/10 models (60%)

⚠️  STATUS: BEHIND SCHEDULE

Parse rate is 1 model(s) behind Day 5 projection.

ACTION REQUIRED:
[... detailed action options ...]
```

### Investigation

```bash
# Test implemented features in isolation
$ pytest tests/synthetic/ -v

# Results: All synthetic tests passing ✅
# Conclusion: Features work correctly, models failing for other reasons
```

### Analysis

Review each failed model:

1. **circle.gms** - Blocker: Nested indexing (not implemented yet)
   - Estimate: 2-3 hours
   - Priority: High (simple, high value)

2. **himmel16.gms** - Blocker: Variable bounds + i++1 bug
   - Estimate: 4-6 hours
   - Priority: Medium (bug fix + feature)

3. **mingamma.gms** - Blocker: Comma-separated scalar declarations
   - Estimate: 3-4 hours
   - Priority: High (planned feature)

4. **maxmin.gms** - Blocker: Complex function calls
   - Estimate: 8-10 hours
   - Priority: Low (already planned to defer)

**Total:** 17-23 hours remaining work vs. 40 hours available

### Decision: Option A (Debug & Fix)

**Rationale:**
- Only 1 model behind Day 5 projection (not critical)
- Remaining work (17-23h) fits well within available time (40h)
- No major surprises or unexpected blockers
- Original sprint plan is sound

**Adjusted plan:**
- Days 6-7: Implement nested indexing for circle.gms (2-3h)
- Days 7-8: Implement comma-separated declarations for mingamma.gms (3-4h)
- Days 8-9: Debug i++1 + variable bounds for himmel16.gms (4-6h)
- Day 10: Testing, documentation, buffer time
- Defer: maxmin.gms to Sprint 11 (as planned)

**Expected outcome:** 90% parse rate (9/10 models) by Day 10 ✅

### Documentation

```bash
# Update sprint log
$ echo "Day 5 Checkpoint: 60% parse rate, proceeding with Option A" >> \
    docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md

# Commit decision
$ git add docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md
$ git commit -m "Day 5 checkpoint: On track with minor delay"
```

## Best Practices

### Before Checkpoint

1. **Commit all work in progress**
   - Clean working directory
   - All implemented features committed
   - No uncommitted experiments

2. **Run full test suite**
   ```bash
   make test
   ```
   - Verify no regressions
   - All tests passing

3. **Update sprint log**
   - Document completed features
   - Note any issues encountered

### During Checkpoint

1. **Run checkpoint script first**
   ```bash
   ./scripts/sprint10_checkpoint.sh
   ```
   - Get high-level status

2. **Investigate failures thoroughly**
   - Don't rush to conclusions
   - Test features in isolation
   - Review implementation vs. specification

3. **Discuss with team (if applicable)**
   - Share checkpoint results
   - Get input on decision
   - Consider multiple perspectives

### After Checkpoint

1. **Document decision**
   - Record in sprint log
   - Explain rationale
   - Update plans if pivoting

2. **Execute decision quickly**
   - Don't overthink
   - Commit to chosen strategy
   - Start execution same day

3. **Re-validate periodically**
   - Run parse rate measurement daily
   - Adjust if new information emerges
   - Stay flexible

## Technical Details

### Parse Rate Calculation

```python
# From scripts/measure_parse_rate.py
successful = sum(1 for _, success in results if success)
total = len(results)
percentage = (successful / total * 100) if total > 0 else 0.0
```

**GAMSLIB Tier 1 models (10 total):**
1. circle.gms
2. himmel16.gms
3. hs62.gms
4. mathopt1.gms
5. maxmin.gms
6. mhw4d.gms
7. mhw4dx.gms
8. mingamma.gms
9. rbrock.gms
10. trig.gms

### Checkpoint Thresholds

| Metric | Value | Description |
|--------|-------|-------------|
| Baseline | 60% (6/10) | Sprint 10 starting point |
| Day 5 Target | 70% (7/10) | Minimum expected progress |
| Sprint Goal | 90% (9/10) | Final target (defer maxmin.gms) |
| Stretch Goal | 100% (10/10) | Include maxmin.gms |

**Linear projection:**
- Day 0: 60% (6 models)
- Day 5: 70% (7 models) - +1 model
- Day 10: 90% (9 models) - +2 more models

**Why Day 5 = 70%?**
- Assumes roughly linear progress
- Accounts for mid-sprint acceleration (momentum)
- Provides early warning with enough time to adjust
- Not too aggressive (allows for complexity variations)

### Exit Codes

**measure_parse_rate.py:**
- `0`: All models parsed successfully (100%)
- `1`: Some models failed (< 100%)

**sprint10_checkpoint.sh:**
- `0`: On track or ahead (≥ 70%)
- `1`: Behind schedule (< 70%)

### Integration with CI/CD

The checkpoint script can be integrated into CI workflows:

```yaml
# Example GitHub Actions workflow
name: Sprint 10 Checkpoint
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:      # Manual trigger

jobs:
  checkpoint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run checkpoint
        run: ./scripts/sprint10_checkpoint.sh
```

## Troubleshooting

### Script Fails to Run

**Symptom:** `./scripts/sprint10_checkpoint.sh: Permission denied`

**Solution:**
```bash
chmod +x scripts/sprint10_checkpoint.sh
chmod +x scripts/measure_parse_rate.py
```

### Cannot Parse Output

**Symptom:** `ERROR: Could not parse output from measure_parse_rate.py`

**Causes:**
1. measure_parse_rate.py crashed
2. Output format changed
3. Python import errors

**Debug:**
```bash
# Run parse rate script directly to see error
python scripts/measure_parse_rate.py --verbose

# Check Python environment
python --version  # Should be 3.11+
pip list | grep nlp2mcp
```

### Models Not Found

**Symptom:** `⚠️  circle.gms - FILE NOT FOUND`

**Solution:**
```bash
# Verify GAMSLIB directory exists
ls -la tests/fixtures/gamslib/

# Check for specific model
ls -la tests/fixtures/gamslib/circle.gms

# If missing, check if in correct directory
pwd  # Should be project root
```

### Unexpected Parse Rate

**Symptom:** Parse rate doesn't match expectations (e.g., shows 50% when expecting 60%)

**Debug steps:**
1. Run verbose mode: `python scripts/measure_parse_rate.py --verbose`
2. Check which models are failing
3. Compare to previous test runs
4. Look for regressions in previously passing models
5. Verify recent commits didn't break functionality

## Summary

The Sprint 10 checkpoint system provides:

✅ **Early warning system** - Detect issues at Day 5 instead of Day 10  
✅ **Informed decision-making** - Data-driven strategy adjustments  
✅ **Multiple options** - Debug, pivot, or reduce scope based on situation  
✅ **Clear guidance** - Structured framework for making decisions  
✅ **Automation** - Scripts handle measurement and analysis  

**Key takeaway:** The checkpoint is a tool for course correction, not a pass/fail test. Use it to make informed decisions and maximize sprint success.
