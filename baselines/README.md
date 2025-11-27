# Performance Baselines

This directory contains performance baselines for tracking CI performance and regression detection.

## Directory Structure

```
baselines/
  performance/
    rolling/         # Latest baselines from main branch (not git-tracked)
    golden/          # Sprint milestone snapshots (git-tracked)
  parse_rate/        # Parse rate baselines (git-tracked)
```

## Baseline Format

Each baseline is stored as a JSON file with the following structure:

```json
{
  "model": "circle.gms",
  "parse_rate": 1.0,
  "convert_rate": 1.0,
  "parse_time_ms": 45,
  "total_time_ms": 443,
  "commit": "abc1234",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Fields

- `model`: Model filename (e.g., "circle.gms")
- `parse_rate`: Parse success rate (0.0 to 1.0)
- `convert_rate`: Conversion success rate (0.0 to 1.0)
- `parse_time_ms`: Parsing time in milliseconds
- `total_time_ms`: Total processing time in milliseconds
- `commit`: Git commit SHA
- `timestamp`: ISO 8601 timestamp

## Usage

### Rolling Baselines

Rolling baselines are updated on every main branch push. They track the latest performance metrics and are used for regression detection in pull requests.

**Not tracked in git** - generated dynamically.

### Golden Baselines

Golden baselines are snapshots taken at sprint milestones. They provide long-term historical tracking and are used for sprint-to-sprint comparisons.

**Tracked in git** - committed at milestone checkpoints.

### Parse Rate Baselines

Parse rate baselines track parsing success rates across the GAMS model library. Used to detect regressions in parser functionality.

**Tracked in git** - updated when parser changes affect success rates.

## Thresholds

Performance comparison thresholds:

- **20% slower**: Warning logged, CI passes
- **50% slower**: CI fails

Parse/convert rate thresholds (to be implemented in Day 8):

- **5% drop**: Warning logged
- **10% drop**: CI fails
