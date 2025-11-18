# Partial Parse Metric Fixtures

This directory contains test fixtures for partial parse metric calculation and missing feature extraction.

## Purpose

These fixtures test the parser's ability to calculate parse percentage and identify missing features for models that partially parse.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with known partial parse scenario
- `expected_results.yaml` - Expected parse percentage and missing features

## Coverage

Target: 3 partial parse fixtures covering:
- Partial parse with lead/lag indexing error (himmel16 pattern)
- Partial parse with function call error (circle pattern)
- Complete success baseline (100% parse)

## Fixture List

1. **01_himmel16_pattern.gms** - Partial parse ~80% (i++1 indexing missing)
   - Tests lead/lag indexing blocker (i++1, i--1)
   - Expected to fail at equation definition
   - Missing feature: "Lead/lag indexing (i++1, i--1)"

2. **02_circle_pattern.gms** - Partial parse ~70% (function calls missing)
   - Tests function call in assignment blocker
   - Expected to fail at parameter assignment with uniform()
   - Missing feature: "Function calls in assignments"

3. **03_complete_success.gms** - 100% parse baseline
   - Tests successful complete parse
   - No missing features
   - Validates 100% parse percentage reporting

## Usage

```bash
# Parse all partial parse fixtures with metrics
for f in tests/fixtures/partial_parse/*.gms; do 
    python -m src.cli parse "$f" --show-metrics
done
```

## Expected Results

- **100% Parse:** 1/3 (fixture 03)
- **Partial Parse:** 2/3 (fixtures 01, 02)

See `expected_results.yaml` for detailed expectations.

## Status

- **Created:** Sprint 8 Day 9
- **Fixtures:** 3/3 ✓
- **Coverage:**
  - ✅ Partial parse with lead/lag indexing
  - ✅ Partial parse with function calls
  - ✅ 100% parse baseline

## Notes

Partial parse metrics enable tracking incremental progress toward 100% parse rate. Dashboard will display: "himmel16: 85% parsed, needs [i++1 indexing]".

These fixtures validate the line counting and missing feature extraction logic implemented in Sprint 8 Day 7.
