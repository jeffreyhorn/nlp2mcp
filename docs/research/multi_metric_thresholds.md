# Multi-Metric CI Threshold Patterns - Research

**Date:** 2025-11-29  
**Sprint:** Epic 2 - Sprint 12 Prep Task 4  
**Purpose:** Research best practices for multi-metric CI threshold checking

---

## Executive Summary

**Problem:** Sprint 11 added CLI arguments for multi-metric thresholds but didn't implement the backend logic. This technical debt must be resolved in Sprint 12 Component 2.

**Solution:** Extend `check_parse_rate_regression.py` to support 3 metrics (parse_rate, convert_rate, performance) with dual thresholds (warn/fail) per metric.

**Key Decisions:**
- **Exit code strategy:** Option B - Check all metrics, exit with worst status
- **Metrics architecture:** Extend existing `check_parse_rate_regression.py` script
- **Thresholds:** parse_rate (5%/10%), convert_rate (5%/10%), performance (20%/50%)
- **PR comment format:** Table with ✅/⚠️/❌ status indicators

---

## Survey of Existing Tools

### 1. Lighthouse CI

**Tool:** Google's Lighthouse CI for performance budgets  
**URL:** https://github.com/GoogleChrome/lighthouse-ci

**Key Patterns:**

**Multi-Metric Support:**
- Lighthouse CI supports checking multiple performance metrics simultaneously (FCP, LCP, TTI, CLS, etc.)
- Each metric can have independent thresholds configured in `lighthouserc.json`
- Configuration format:
  ```json
  {
    "ci": {
      "assert": {
        "assertions": {
          "first-contentful-paint": ["warn", {"maxNumericValue": 2000}],
          "largest-contentful-paint": ["error", {"maxNumericValue": 4000}],
          "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}]
        }
      }
    }
  }
  ```

**Exit Code Strategy:**
- **Exit 0:** All assertions pass
- **Exit 1:** One or more assertions fail
- **Key insight:** Lighthouse CI checks ALL assertions before exiting, reporting worst status
- Assertions can be marked as "warn" or "error" severity levels

**Reporting:**
- Generates detailed HTML reports with all metrics
- Shows pass/fail status for each metric with color coding
- Displays current value vs threshold for each metric
- PR comments show summary table with all metrics

**Lessons Learned:**
- ✅ Check all metrics before failing (don't fast-fail on first threshold)
- ✅ Support warn vs error severity levels
- ✅ Show all metrics in summary table for easy comparison
- ✅ Use exit code 1 for failures (standard Unix convention)

---

### 2. pytest-benchmark

**Tool:** Python benchmarking plugin for pytest  
**URL:** https://github.com/ionelmc/pytest-benchmark

**Key Patterns:**

**Multi-Metric Support:**
- Tracks multiple timing metrics per benchmark (min, max, mean, median, stddev)
- Supports comparison against previous benchmark runs
- Configuration via `--benchmark-compare-fail=EXPR` flag
- Example: `--benchmark-compare-fail=mean:10%` fails if mean time increased >10%

**Exit Code Strategy:**
- **Exit 0:** All benchmarks pass thresholds
- **Exit 1:** One or more benchmarks exceed thresholds
- Uses pytest's standard exit codes (see pytest documentation)
- **Key insight:** Integrates with pytest's existing failure handling

**Reporting:**
- Generates comparison tables showing all benchmark metrics
- Shows baseline vs current with % change
- Color codes regressions (red) vs improvements (green)
- Can output JSON for CI integration

**Thresholds:**
- Default threshold: 200% (2x slowdown triggers alert)
- Configurable per-metric thresholds
- Supports both absolute and relative thresholds

**Lessons Learned:**
- ✅ Support relative thresholds (% change) not just absolute values
- ✅ Show all metrics in comparison table
- ✅ Use standard exit codes (0 = pass, 1 = fail)
- ✅ Export structured data (JSON) for programmatic consumption

---

### 3. Codecov

**Tool:** Code coverage tracking and reporting  
**URL:** https://docs.codecov.com/docs/commit-status

**Key Patterns:**

**Multi-Metric Support:**
- Tracks coverage across multiple dimensions (project, patch, files, flags)
- Each dimension can have independent thresholds
- Configuration in `codecov.yml`:
  ```yaml
  coverage:
    status:
      project:
        default:
          target: auto
          threshold: 5%
      patch:
        default:
          target: 90%
          threshold: 0%
  ```

**Exit Code Strategy:**
- Does not directly control CI exit codes
- Instead, posts GitHub status checks that can block merges
- **Key insight:** Decouples threshold checking from CI workflow
- Status checks can be "success", "failure", or "error"

**Thresholds:**
- **target:** Minimum coverage required (absolute or "auto" for comparison)
- **threshold:** Allowable wiggle room (e.g., 5% = coverage can drop by 5%)
- Supports both absolute targets (80%) and relative targets (auto)

**Reporting:**
- Posts detailed PR comments with coverage changes
- Shows coverage delta for each file
- Highlights files with significant coverage drops
- Provides links to detailed reports

**Lessons Learned:**
- ✅ Support "auto" mode that compares to baseline (relative thresholds)
- ✅ Allow "wiggle room" threshold to account for flaky metrics
- ⚠️ GitHub status checks are more complex than exit codes
- ✅ Detailed per-file reporting helps diagnose issues

---

## Exit Code Strategy

### Options Considered

**Option A: Fast-Fail (Exit on First Threshold Violation)**

**Pros:**
- Faster execution (stops on first failure)
- Simple implementation

**Cons:**
- Developer doesn't see full picture (which other metrics failed?)
- Poor UX - multiple CI runs needed to fix all issues
- Violates "check all, report all" principle

**Verdict:** ❌ Rejected

---

**Option B: Check All Metrics, Exit with Worst Status** ✅ RECOMMENDED

**Pros:**
- Developer sees all failures in single CI run
- Follows Lighthouse CI pattern
- Better UX - fix all issues at once
- Supports warn vs fail distinction

**Cons:**
- Slightly slower (must check all metrics)
- More complex exit code logic

**Verdict:** ✅ SELECTED - Best UX and industry standard pattern

**Exit Code Mapping:**
- **0 (SUCCESS):** All metrics pass (or only warnings present)
- **1 (FAILURE):** One or more metrics exceed FAIL threshold
- **2 (ERROR):** Invalid arguments, missing files, JSON parse errors

**Severity Levels:**
- **PASS:** Metric within acceptable range (no threshold exceeded)
- **WARN:** Metric exceeds warn threshold but not fail threshold
- **FAIL:** Metric exceeds fail threshold

**Exit Code Decision Logic:**
```python
# Pseudocode
worst_status = "PASS"

for metric in [parse_rate, convert_rate, performance]:
    status = check_metric(metric)
    if status == "FAIL":
        worst_status = "FAIL"
    elif status == "WARN" and worst_status == "PASS":
        worst_status = "WARN"

if worst_status == "FAIL":
    sys.exit(1)
elif worst_status == "WARN":
    # Warn but don't fail
    sys.exit(0)
else:
    sys.exit(0)
```

---

**Option C: Configurable (--fail-fast flag)**

**Pros:**
- Maximum flexibility
- Can optimize for speed when needed

**Cons:**
- More complexity
- Requires documenting two modes
- Default behavior still unclear

**Verdict:** ❌ Deferred - Adds complexity without clear benefit

---

## Unified Metrics Architecture

### Current State (Sprint 11)

**Existing Scripts:**
- `scripts/measure_parse_rate.py` - Generates GAMSLib ingestion reports
- `scripts/check_parse_rate_regression.py` - Checks parse rate thresholds (has multi-metric CLI args but not implemented)

**Current Flow:**
```
measure_parse_rate.py
  → reports/gamslib_ingestion_sprintX.json
  → check_parse_rate_regression.py --current report.json --baseline origin/main
```

**JSON Schema (Current):**
```json
{
  "kpis": {
    "parse_rate_percent": 100.0,
    "convert_rate_percent": 85.0,  // Sprint 11 Day 8+
    "avg_time_ms": 23.5             // Sprint 11 Day 8+
  },
  "models": [...]
}
```

### Design Options

**Option A: Extend check_parse_rate_regression.py** ✅ RECOMMENDED

**Approach:**
- Add multi-metric checking logic to existing script
- Remove "not yet implemented" warning
- Implement check_all_metrics() function
- Support both legacy (--threshold) and new (--parse-warn/--parse-fail) modes

**Pros:**
- Minimal code changes
- Backward compatible with Sprint 11 CI workflows
- All logic in one place
- CLI args already exist

**Cons:**
- Script name is now misleading ("parse_rate" but checks 3 metrics)
- Could consider renaming in future

**Verdict:** ✅ SELECTED - Simplest path, backward compatible

---

**Option B: Create New Orchestrator Script**

**Approach:**
- Create `scripts/check_multi_metric_regression.py`
- Keep `check_parse_rate_regression.py` for legacy support
- New script calls measure_parse_rate.py internally

**Pros:**
- Clean separation of concerns
- Clear naming

**Cons:**
- Duplication of code
- Two scripts to maintain
- Migration complexity

**Verdict:** ❌ Rejected - Unnecessary complexity

---

**Option C: Extend measure_parse_rate.py**

**Approach:**
- Add threshold checking to measurement script
- Combine measurement + checking in one script

**Pros:**
- Single script for everything
- Simpler CI workflow

**Cons:**
- Violates single responsibility principle
- Harder to test
- Mixes data collection with policy enforcement

**Verdict:** ❌ Rejected - Poor separation of concerns

---

### Selected Architecture: Extend check_parse_rate_regression.py

**Implementation Plan:**

1. **Add metrics extraction function:**
   ```python
   def read_baseline_metrics_from_git(baseline_ref: str, report_path: str) -> dict[str, float]:
       """Read all metrics from baseline git ref."""
       # Similar to existing read_baseline_from_git but returns dict
   ```

2. **Add multi-metric checking function:**
   ```python
   def check_all_metrics(
       current_metrics: dict[str, float],
       baseline_metrics: dict[str, float],
       thresholds: dict[str, tuple[float, float]]  # (warn, fail) per metric
   ) -> list[MetricResult]:
       """Check all metrics against thresholds."""
   ```

3. **Add MetricResult data class:**
   ```python
   @dataclass
   class MetricResult:
       metric_name: str
       current_value: float
       baseline_value: float
       threshold_warn: float
       threshold_fail: float
       status: Literal["PASS", "WARN", "FAIL"]
       relative_change: float
   ```

4. **Update main() logic:**
   ```python
   if any multi-metric args provided:
       # Use new multi-metric mode
       results = check_all_metrics(current, baseline, thresholds)
       print_results_table(results)
       sys.exit(determine_exit_code(results))
   else:
       # Use legacy single-metric mode (backward compatible)
       ...existing code...
   ```

**Backward Compatibility:**
- If no `--parse-warn/--parse-fail` args provided, use legacy `--threshold` mode
- Legacy mode checks only parse_rate with single threshold
- Multi-metric mode activates when any `--*-warn/--*-fail` arg provided
- Both modes can coexist in same script

---

## PR Comment Format

### Design Goals

1. **Actionable:** Show which metrics failed and by how much
2. **Clear:** Use visual indicators (✅/⚠️/❌) for quick scanning
3. **Complete:** Show all metrics even if some pass
4. **Contextual:** Include threshold values and baselines

### Selected Format

```markdown
## 📊 Multi-Metric Regression Check

| Metric | Status | Current | Baseline | Change | Thresholds (Warn/Fail) |
|--------|--------|---------|----------|--------|------------------------|
| Parse Rate | ✅ PASS | 100.0% | 100.0% | +0.0% | 5% / 10% |
| Convert Rate | ⚠️ WARN | 82.5% | 87.0% | -5.2% | 5% / 10% |
| Performance | ❌ FAIL | 45.2ms | 23.5ms | +92.3% | 20% / 50% |

**Overall Status:** ❌ FAILED (1 metric exceeded fail threshold)

### Details

**⚠️ Convert Rate Warning**
- Current: 82.5% (33/40 models)
- Baseline: 87.0% (35/40 models)
- Change: -5.2% (exceeded 5% warn threshold)
- Recommendation: Review converter changes

**❌ Performance Failure**
- Current: 45.2ms average
- Baseline: 23.5ms average
- Change: +92.3% (exceeded 50% fail threshold)
- Recommendation: Profile and optimize parser

---

<details>
<summary>View full report</summary>

[Link to detailed JSON report](../../reports/gamslib_ingestion_sprint12.json)
</details>
```

### Alternative Formats Considered

**Compact Format (Rejected):**
```
Parse Rate: ✅ 100% (100% baseline, +0.0%)
Convert Rate: ⚠️ 82.5% (87% baseline, -5.2%)
Performance: ❌ 45.2ms (23.5ms baseline, +92.3%)
```
- **Pros:** More compact
- **Cons:** Harder to scan, no threshold visibility

**Detailed Format (Too Verbose):**
- Shows histogram of per-model results
- Full JSON diff
- **Cons:** Too long for PR comments

**Selected Rationale:** Table format balances information density with readability.

---

## Threshold Value Selection

### Metric 1: Parse Rate

**Recommended Thresholds:**
- **Warn:** 5% regression
- **Fail:** 10% regression

**Rationale:**
- Parse rate is primary quality metric
- 5% warn = early signal (e.g., 100% → 95% = 2 models on Tier 1)
- 10% fail = hard stop (e.g., 100% → 90% = 4 models)
- Thresholds match existing `--threshold 0.10` default

**Example:**
- Baseline: 100% (40/40 models)
- Current: 95% (38/40 models)
- Change: -5% → ⚠️ WARN
- Current: 88% (35/40 models)
- Change: -12% → ❌ FAIL

---

### Metric 2: Convert Rate

**Recommended Thresholds:**
- **Warn:** 5% regression
- **Fail:** 10% regression

**Rationale:**
- Convert rate added in Sprint 11 Day 8
- Similar criticality to parse rate
- Same thresholds for consistency
- 5% = 2 models on Tier 1 (40 models)

**Example:**
- Baseline: 87.5% (35/40 models)
- Current: 82.5% (33/40 models)
- Change: -5.7% → ⚠️ WARN

**Future Recalibration:**
- Monitor Sprint 12-13 for convert rate stability
- May need to relax thresholds if metric proves flaky
- Document recalibration decisions in Sprint retrospectives

---

### Metric 3: Performance (avg_time_ms)

**Recommended Thresholds:**
- **Warn:** 20% regression
- **Fail:** 50% regression

**Rationale:**
- Performance more variable than parse/convert rates
- 20% warn = noticeable slowdown (23ms → 28ms)
- 50% fail = severe regression (23ms → 35ms)
- Looser thresholds account for system noise

**Example:**
- Baseline: 23.5ms average
- Current: 28.2ms average
- Change: +20.0% → ⚠️ WARN
- Current: 42.0ms average
- Change: +78.7% → ❌ FAIL

**Considerations:**
- Performance varies by system (M1 Mac vs GitHub Actions runner)
- May need to use baseline comparison rather than absolute values
- Consider P95 or P99 instead of average in future

---

### Threshold Methodology

**Approach: Relative Thresholds (% change from baseline)**

**Formula (Metric-Specific):**

For metrics where **higher is better** (e.g., `parse_rate`, `convert_rate`):
```
relative_change = (baseline - current) / baseline
status = FAIL if relative_change > fail_threshold
status = WARN if relative_change > warn_threshold
status = PASS otherwise
```

For metrics where **lower is better** (e.g., `avg_time_ms`):
```
relative_change = (current - baseline) / baseline
status = FAIL if relative_change > fail_threshold
status = WARN if relative_change > warn_threshold
status = PASS otherwise
```

**Why Relative vs Absolute:**
- ✅ Works across sprints as absolute values change
- ✅ Accounts for different model sets (Tier 1 vs Tier 2)
- ✅ Self-adjusting as baseline improves
- ❌ Can be confusing if baseline near 0%

**Edge Cases:**
- If baseline = 0%, cannot regress (always PASS)
- If current > baseline, improvement (always PASS)
- If baseline < warn_threshold, warn threshold may be too sensitive

**Recalibration Strategy:**
- Review thresholds after Sprint 12
- Analyze historical regression data
- Adjust if too many false positives (flaky) or negatives (missed regressions)
- Document threshold changes in CHANGELOG.md

---

## Implementation Checklist for Sprint 12

### Component 2: Multi-Metric CI Thresholds (Days 4-6)

- [ ] **Day 4: Extend check_parse_rate_regression.py**
  - [ ] Add `MetricResult` dataclass
  - [ ] Add `read_baseline_metrics_from_git()` function
  - [ ] Add `check_all_metrics()` function
  - [ ] Add `determine_exit_code()` function
  - [ ] Update `main()` to support multi-metric mode
  - [ ] Remove "not yet implemented" warning
  - [ ] Maintain backward compatibility with `--threshold` arg

- [ ] **Day 5: Implement PR comment generation**
  - [ ] Add `format_results_table()` function (Markdown table)
  - [ ] Add `format_details_section()` function (per-metric details)
  - [ ] Add `--output-format` arg (console, markdown, json)
  - [ ] Test table rendering with various statuses

- [ ] **Day 6: Testing and documentation**
  - [ ] Add unit tests for `check_all_metrics()`
  - [ ] Add integration test with all 3 metrics
  - [ ] Test backward compatibility with legacy mode
  - [ ] Test edge cases (0% baseline, improvements, all fail)
  - [ ] Update script docstring with multi-metric examples
  - [ ] Update CI workflow to use multi-metric args

### Quality Gates

- [ ] All tests pass (make test)
- [ ] Type checking passes (make typecheck)
- [ ] Linting passes (make lint)
- [ ] Backward compatible with Sprint 11 CI workflows
- [ ] PR comment renders correctly on GitHub

---

## Unknowns Resolved

### Unknown 2.1: Metric Selection and Prioritization

**Resolution:** ✅ VERIFIED

**Selected Metrics:**
1. **parse_rate** - Percentage of models that parse successfully
2. **convert_rate** - Percentage of parsed models that convert to IR
3. **performance** - Average parse time in milliseconds (avg_time_ms)

**Prioritization:**
- **parse_rate:** Highest priority (primary quality metric)
- **convert_rate:** Medium priority (secondary quality metric)
- **performance:** Lowest priority (optimization metric, not correctness)

**Deferred Metrics:**
- Memory usage (complexity of measurement)
- Per-model performance (too granular for CI)
- Code coverage (separate pytest-cov integration)

**Decision Rationale:**
- Focus on metrics already in JSON output (no new instrumentation)
- Prioritize correctness (parse/convert) over performance
- Keep metric count manageable (3 metrics = sweet spot)

---

### Unknown 2.2: Threshold Setting Methodology

**Resolution:** ✅ VERIFIED

**Threshold Values:**
- **parse_rate:** warn=5%, fail=10%
- **convert_rate:** warn=5%, fail=10%
- **performance:** warn=20%, fail=50%

**Methodology: Relative Thresholds (% change from baseline)**
- Formula: `(baseline - current) / baseline > threshold`
- Accounts for changing baselines across sprints
- Self-adjusting as absolute performance improves

**Recalibration Strategy:**
- Monitor false positive/negative rates in Sprint 12-13
- Adjust thresholds if metrics prove flaky
- Document changes in Sprint retrospectives
- Consider tightening thresholds as parser stabilizes

**Why Not Absolute Thresholds:**
- Absolute values change as model set evolves (Tier 1 → Tier 2)
- Hard to maintain across sprints
- Less flexible as project matures

---

### Unknown 2.3: CI Integration Architecture

**Resolution:** ✅ VERIFIED

**Selected Architecture:** Extend `check_parse_rate_regression.py`

**Integration Points:**
1. **Script Extension:**
   - Add multi-metric checking logic to existing script
   - Activate via `--parse-warn/--parse-fail` args (not `--threshold`)
   - Maintain backward compatibility with legacy mode

2. **CI Workflow Update (.github/workflows/ci.yml):**
   ```yaml
   - name: Check Multi-Metric Regressions
     run: |
       python scripts/check_parse_rate_regression.py \
         --current reports/gamslib_ingestion_sprint12.json \
         --baseline origin/main \
         --parse-warn 0.05 --parse-fail 0.10 \
         --convert-warn 0.05 --convert-fail 0.10 \
         --perf-warn 0.20 --perf-fail 0.50
   ```

3. **PR Comment Integration:**
   - Generate Markdown table in script
   - Post via GitHub Actions (separate step)
   - Use `--output-format markdown` flag

**Compatibility with pytest:**
- `check_parse_rate_regression.py` runs independently of pytest
- No pytest plugin required
- pytest runs separately for unit/integration tests

---

### Unknown 2.4: Backward Compatibility with Sprint 11

**Resolution:** ✅ VERIFIED

**Compatibility Strategy:**

**Scenario 1: Legacy Mode (Sprint 11 CI)**
```bash
# Sprint 11 workflow (still works)
python scripts/check_parse_rate_regression.py \
  --current reports/gamslib_ingestion.json \
  --baseline origin/main \
  --threshold 0.10
```
- ✅ Uses existing check_regression() logic
- ✅ Checks only parse_rate
- ✅ Exit code 0/1 unchanged
- ✅ No breaking changes

**Scenario 2: Multi-Metric Mode (Sprint 12+)**
```bash
# Sprint 12 workflow
python scripts/check_parse_rate_regression.py \
  --current reports/gamslib_ingestion.json \
  --baseline origin/main \
  --parse-warn 0.05 --parse-fail 0.10 \
  --convert-warn 0.05 --convert-fail 0.10 \
  --perf-warn 0.20 --perf-fail 0.50
```
- ✅ Uses new check_all_metrics() logic
- ✅ Checks 3 metrics
- ✅ Exit code 0/1/2
- ✅ Activates only if multi-metric args provided

**Transition Plan:**
1. Sprint 12 Day 4: Implement multi-metric logic
2. Sprint 12 Day 5: Test both modes side-by-side
3. Sprint 12 Day 6: Update CI workflow to use multi-metric mode
4. Sprint 13+: Deprecate legacy mode (print warning, still functional)
5. Sprint 14+: Remove legacy mode support (breaking change)

**Migration Guide:**
```
# Old (Sprint 11)
--threshold 0.10

# New (Sprint 12+)
--parse-warn 0.05 --parse-fail 0.10

# Both modes work in Sprint 12 (no forced migration)
```

---

### Unknown 6.3: Integration with Multi-Metric Thresholds (CI Checklist)

**Resolution:** ✅ VERIFIED

**Checklist Item Wording:**

**Sprint 12 PR Template Addition:**
```markdown
## Quality Checklist

### Automated Checks
- [ ] All tests pass (`make test`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Linting passes (`make lint`)
- [ ] **Multi-metric regression check passes** (see CI status below)
  - Parse Rate: Must not regress >10% (warn at 5%)
  - Convert Rate: Must not regress >10% (warn at 5%)
  - Performance: Must not regress >50% (warn at 20%)

### Override Process
If multi-metric check fails:
1. Review CI output for specific metric failures
2. Justify regression in PR description (e.g., "Expected 15% perf regression due to AST refactor")
3. Request explicit approval from maintainer
4. Add `override: metrics` label to PR
5. Document regression in CHANGELOG.md
```

**Link to CI Job Output:**
- GitHub Actions shows check result in PR status
- Click "Details" → View full multi-metric table
- Link to raw JSON report in comment

**Enforcement:**
- CI check is REQUIRED (cannot merge if fails)
- Override process requires maintainer approval
- Label `override: metrics` bypasses CI check
- Overrides logged for post-mortem analysis

---

## References

1. **Lighthouse CI Documentation**
   - https://github.com/GoogleChrome/lighthouse-ci
   - https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/configuration.md

2. **pytest-benchmark**
   - https://github.com/ionelmc/pytest-benchmark
   - https://pytest-benchmark.readthedocs.io/

3. **Codecov**
   - https://docs.codecov.com/docs/commit-status
   - https://docs.codecov.com/docs/common-recipe-list

4. **pytest Exit Codes**
   - https://docs.pytest.org/en/stable/reference/exit-codes.html

5. **Sprint 11 Multi-Metric PR**
   - (Reference Sprint 11 Day 8 PR that added CLI args)

---

## Appendix: Example Outputs

### Example 1: All Metrics Pass

```
$ python scripts/check_parse_rate_regression.py \
    --current reports/current.json \
    --baseline origin/main \
    --parse-warn 0.05 --parse-fail 0.10 \
    --convert-warn 0.05 --convert-fail 0.10 \
    --perf-warn 0.20 --perf-fail 0.50

📊 Multi-Metric Regression Check

Metric           Status    Current   Baseline   Change   Thresholds (Warn/Fail)
---------------  --------  --------  ---------  -------  -----------------------
Parse Rate       ✅ PASS    100.0%     100.0%    +0.0%   5% / 10%
Convert Rate     ✅ PASS     87.5%      87.5%    +0.0%   5% / 10%
Performance      ✅ PASS     22.1ms     23.5ms    -6.0%   20% / 50%

Overall Status: ✅ PASSED (all metrics within thresholds)

Exit code: 0
```

### Example 2: Warn on Convert Rate

```
📊 Multi-Metric Regression Check

Metric           Status    Current   Baseline   Change   Thresholds (Warn/Fail)
---------------  --------  --------  ---------  -------  -----------------------
Parse Rate       ✅ PASS    100.0%     100.0%    +0.0%   5% / 10%
Convert Rate     ⚠️ WARN     82.5%      87.5%    -5.7%   5% / 10%
Performance      ✅ PASS     24.2ms     23.5ms    +3.0%   20% / 50%

Overall Status: ⚠️ WARNING (1 metric exceeded warn threshold)

Details:
⚠️ Convert Rate Warning
- Current: 82.5% (33/40 models)
- Baseline: 87.5% (35/40 models)
- Change: -5.7% (exceeded 5% warn threshold)
- Recommendation: Review converter changes

Exit code: 0 (warnings don't block CI)
```

### Example 3: Fail on Performance

```
📊 Multi-Metric Regression Check

Metric           Status    Current   Baseline   Change   Thresholds (Warn/Fail)
---------------  --------  --------  ---------  -------  -----------------------
Parse Rate       ✅ PASS    100.0%     100.0%    +0.0%   5% / 10%
Convert Rate     ⚠️ WARN     82.5%      87.5%    -5.7%   5% / 10%
Performance      ❌ FAIL     45.2ms     23.5ms   +92.3%   20% / 50%

Overall Status: ❌ FAILED (1 metric exceeded fail threshold)

Details:
⚠️ Convert Rate Warning
- Current: 82.5% (33/40 models)
- Baseline: 87.5% (35/40 models)
- Change: -5.7% (exceeded 5% warn threshold)

❌ Performance Failure
- Current: 45.2ms average
- Baseline: 23.5ms average
- Change: +92.3% (exceeded 50% fail threshold)
- Recommendation: Profile and optimize parser

Exit code: 1 (CI will fail)
```
