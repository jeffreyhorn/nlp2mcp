# Multi-Dimensional Indexing Fixtures

This directory contains test fixtures for GAMS multi-dimensional set indexing.

## Purpose

These fixtures test the parser's ability to handle multi-dimensional set indexing patterns that are already supported but need comprehensive test coverage.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with multi-dimensional indexing
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 8 multidim fixtures covering:
- 2D indexing: `x(i,j)` (fixtures 01, 05, 08)
- 3D indexing: `y(i,j,k)` (fixture 02)
- 4D indexing: `w(i,j,k,l)` (fixture 06)
- Nested sum patterns (fixtures 02, 03, 04)
- Mixed dimensional structures (fixture 03)
- Partial indexing (fixture 07)
- Bilinear terms with 2D indexing (fixture 08)

## Fixture List

1. **01_simple_2d.gms** - Basic 2D indexing with `x(i,j)` pattern
2. **02_simple_3d.gms** - Basic 3D indexing with `y(i,j,k)` and nested sums
3. **03_mixed_dimensions.gms** - Mix of 1D, 2D, and 3D variables in same model
4. **04_nested_sums.gms** - Nested summation patterns over 2D variables
5. **05_transportation.gms** - Classic transportation problem (2D supply/demand)
6. **06_4d_indexing.gms** - Four-dimensional indexing `w(i,j,k,l)`
7. **07_partial_indexing.gms** - Variables with partial index overlap
8. **08_bilinear_2d.gms** - Bilinear terms with 2D indexing (regression test)

## Usage

These fixtures are used to verify multi-dimensional indexing support works correctly:

```bash
# Parse all multidim fixtures
for f in tests/fixtures/multidim/*.gms; do python -m src.cli parse "$f"; done
```

## Status

- **Created:** Sprint 7 Day 0
- **Populated:** Sprint 7 Day 8
- **Fixtures:** 8/8 ✓

## Notes

Multi-dimensional indexing already works in the parser (verified in Unknown 1.6 from KNOWN_UNKNOWNS.md). These fixtures provide regression testing and documentation of supported patterns.
