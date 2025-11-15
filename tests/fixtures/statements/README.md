# Statement Syntax Fixtures

This directory contains test fixtures for various GAMS statement patterns.

## Purpose

These fixtures test the parser's ability to handle various GAMS statement types and syntax patterns.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with statement patterns
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 9 statement fixtures covering:
- Multiple scalar declarations: `Scalars a, b, c;`
- Models keyword: `Models` (plural)
- Assignment statements
- Declaration patterns
- Other statement types

## Usage

```bash
# Run statement fixture tests
pytest tests/fixtures/statements/ -v
```

## Status

- **Created:** Sprint 7 Day 0
- **Fixtures:** 0/9 (to be created in Day 9)
