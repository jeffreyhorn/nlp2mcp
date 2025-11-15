# Preprocessor Directive Fixtures

This directory contains test fixtures for GAMS preprocessor directive handling.

## Purpose

These fixtures test the parser's ability to handle GAMS preprocessor directives including:
- `$if not set` conditionals
- `%macro%` expansion
- `$eolCom` end-of-line comment directives
- Other preprocessor features

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with preprocessor directives
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 9 preprocessor fixtures covering:
- Conditional set declarations
- Macro expansion (user-defined and system macros)
- End-of-line comment handling
- Edge cases and error conditions

## Usage

```bash
# Run preprocessor fixture tests
pytest tests/fixtures/preprocessor/ -v
```

## Status

- **Created:** Sprint 7 Day 0
- **Fixtures:** 0/9 (to be created in Day 5)
