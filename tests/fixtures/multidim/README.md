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
- 2D indexing: `x(i,j)`
- 3D indexing: `y(i,j,k)`
- Nested indexing patterns
- Mixed dimensional structures
- Edge cases and complex patterns

## Usage

```bash
# Run multidim fixture tests
pytest tests/fixtures/multidim/ -v
```

## Status

- **Created:** Sprint 7 Day 0
- **Fixtures:** 0/8 (to be created in Day 8)

## Notes

Multi-dimensional indexing already works in the parser (verified in Unknown 1.6 from KNOWN_UNKNOWNS.md). These fixtures provide regression testing and documentation of supported patterns.
