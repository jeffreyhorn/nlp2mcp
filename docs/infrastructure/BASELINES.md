# Baseline Storage Infrastructure

## Overview

This document describes the baseline storage infrastructure for the nlp2mcp project. Baselines are used for regression testing to ensure that changes to the codebase do not degrade quality metrics.

## Directory Structure

```
baselines/
├── simplification/          # Term reduction (simplification) baselines
│   ├── README.md           # Simplification baseline format documentation
│   └── baseline_sprint*.json  # Sprint-specific simplification baselines
├── multi_metric/           # Multi-metric (parse/convert/performance) baselines
│   ├── README.md           # Multi-metric baseline format documentation
│   └── baseline_sprint*.json  # Sprint-specific multi-metric baselines
└── performance/            # Legacy performance baselines
    └── golden/
        └── sprint*_day*.json  # Historical performance snapshots
```

## Baseline Types

### 1. Simplification Baselines

**Location**: `baselines/simplification/`

**Purpose**: Track algebraic simplification effectiveness metrics (operation count and term count reduction)

**Schema**: JSON format (v1.0.0) with per-model and aggregate metrics

**Key Metrics**:
- Operation count before/after simplification
- Term count before/after simplification  
- Reduction percentages
- Execution time
- Fixpoint iterations
- Transformations applied

**File Naming**: `baseline_sprint<N>.json` (e.g., `baseline_sprint11.json`)

**Documentation**: See `baselines/simplification/README.md` for complete schema specification

**Update Cadence**: Create new baseline when:
- Adding/modifying/removing transformations
- Changing IR structure
- Major refactoring of simplification engine

**CI Usage**: Used for regression testing during Sprint 12+ to ensure simplification effectiveness is maintained

### 2. Multi-Metric Baselines

**Location**: `baselines/multi_metric/`

**Purpose**: Track parse rate, convert rate, and performance metrics for comprehensive quality assurance

**Schema**: JSON format (v1.0.0) with per-model and aggregate metrics

**Key Metrics**:
- Parse rate (successfully parsed / total models)
- Convert rate (successfully converted / total models)
- Parse time (ms)
- Total time (ms)
- P95 latencies

**File Naming**: `baseline_sprint<N>.json` (e.g., `baseline_sprint12.json`)

**Documentation**: See `baselines/multi_metric/README.md` for complete schema specification

**Threshold Configuration**:
- Parse rate: Warn 5% degradation, Fail 10% degradation
- Convert rate: Warn 5% degradation, Fail 10% degradation
- Performance: Warn 20% degradation, Fail 50% degradation

**Update Cadence**: Create new baseline when:
- Baseline invalidation threshold reached (>10% improvement)
- Major IR changes affecting parse/convert rates
- End of sprint checkpoints

**CI Usage**: Multi-metric regression check with warn/fail thresholds

**Backward Compatibility**: Compatible with legacy `baselines/performance/golden/` format (uses same "summary" field name, extends with additional metrics)

### 3. Legacy Performance Baselines

**Location**: `baselines/performance/golden/`

**Purpose**: Historical performance snapshots from Sprint 11 and earlier

**File Naming**: `sprint<N>_day<D>.json` (e.g., `sprint11_day6.json`)

**Status**: Maintained for backward compatibility; new baselines use multi_metric format

## Git Tracking

All baseline files are tracked in Git (not Git LFS):
- Small file size (<50KB typical)
- JSON format with stable line endings (LF on all platforms)
- Changes reviewed in PRs like code changes
- Commit messages document baseline updates

## Update Process

### Manual Update

Use the `scripts/update_baselines.sh` script:

```bash
# Update simplification baseline for Sprint 12
./scripts/update_baselines.sh --simplification sprint12

# Update multi-metric baseline for Sprint 12
./scripts/update_baselines.sh --multi-metric sprint12

# Update all baselines for Sprint 12
./scripts/update_baselines.sh --all sprint12

# Dry run to preview changes
./scripts/update_baselines.sh --all sprint12 --dry-run
```

### Automated Update

Baseline updates can be triggered during CI/CD:
- Sprint checkpoint workflows
- Manual workflow dispatch with sprint parameter
- Post-release baseline refresh

### Update Validation

After updating baselines:

1. **Validate JSON format**:
   ```bash
   python3 -c "import json; json.load(open('baselines/simplification/baseline_sprint12.json'))"
   python3 -c "import json; json.load(open('baselines/multi_metric/baseline_sprint12.json'))"
   ```

2. **Verify schema version**:
   ```bash
   jq '.schema_version' baselines/simplification/baseline_sprint12.json
   jq '.sprint' baselines/multi_metric/baseline_sprint12.json
   ```

3. **Check metadata**:
   - Commit SHA is current
   - Timestamp is recent
   - Model counts are expected

4. **Review changes**:
   ```bash
   git diff baselines/
   ```

## CI Integration

### Simplification Regression Check

```bash
# Run simplification analysis and compare to baseline
pytest tests/test_simplification.py --baseline=baselines/simplification/baseline_sprint11.json

# Exit codes:
# 0 = PASS (within thresholds)
# 1 = FAIL (outside thresholds)
```

### Multi-Metric Regression Check

```bash
# Run multi-metric check with thresholds
python scripts/check_multi_metric_regression.py \
  --baseline baselines/multi_metric/baseline_sprint12.json \
  --parse-warn 0.05 --parse-fail 0.10 \
  --convert-warn 0.05 --convert-fail 0.10 \
  --perf-warn 0.20 --perf-fail 0.50

# Exit codes:
# 0 = PASS (all metrics within thresholds)
# 1 = WARN (some metrics at warn threshold)
# 2 = FAIL (some metrics at fail threshold)
```

## Baseline Lifecycle

### Creation

1. Implement feature/change
2. Stabilize metrics
3. Run baseline collection script
4. Review baseline file
5. Commit to repository

### Maintenance

- Monitor baseline drift over time
- Update when invalidation triggers occur
- Document changes in commit messages

### Retirement

- Legacy baselines preserved for historical reference
- Marked as deprecated in README if superseded
- Not deleted to maintain git history

## Schema Versioning

Both baseline types use semantic versioning for schemas:

- **Major version** (x.0.0): Breaking changes to schema structure
- **Minor version** (0.x.0): Backward-compatible additions (new optional fields)
- **Patch version** (0.0.x): Documentation or clarification changes

Current versions:
- Simplification baseline schema: 1.0.0
- Multi-metric baseline schema: 1.0.0

## Related Documentation

- `baselines/simplification/README.md` - Simplification baseline format specification
- `baselines/multi_metric/README.md` - Multi-metric baseline format specification
- `docs/research/term_reduction_measurement.md` - Sprint 12 Prep Task 2 (simplification design)
- `docs/research/multi_metric_thresholds.md` - Sprint 12 Prep Task 4 (threshold design)
- `KNOWN_UNKNOWNS.md` - Unknown 1.2 (Baseline Collection Approach), 1.6 (Baseline Drift Over Time)

## Change History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-30 | Initial baseline infrastructure (Task 9) | Sprint 12 Prep |

## Questions and Support

For questions about baseline infrastructure:
- Review README files in `baselines/simplification/` and `baselines/multi_metric/`
- Check KNOWN_UNKNOWNS.md for open questions about baseline management
- See sprint retrospectives for lessons learned about baseline maintenance
