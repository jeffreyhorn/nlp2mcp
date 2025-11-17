# Statement Fixtures

This directory contains test fixtures for GAMS statement-level features.

## Purpose

These fixtures test the parser's ability to handle various GAMS statements including model declarations, solve statements, scalar assignments, and other statement-level constructs.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with specific statement pattern
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 9 statement fixtures covering:
- Model declarations (`Model m /all/`, `Model m /eq1, eq2/`)
- Solve statements (`solve m using nlp minimizing obj`)
- Scalar assignments (`Scalar pi /3.14159/`, `Scalars a, b, c`)
- Display statements (parser should skip gracefully)
- Option statements (future feature - currently commented out)
- Indexed assignments (error handling for unsupported feature)

## Fixture List

1. **01_model_declaration.gms** - Model declaration with `/all/` syntax
2. **02_solve_basic.gms** - Basic solve statement with nlp solver
3. **03_solve_with_objective.gms** - Solve with explicit objective variable
4. **04_option_statement.gms** - Option statement (not yet supported - commented out)
5. **05_display_statement.gms** - Display statement (parser skips)
6. **06_scalar_assignment.gms** - Scalar declaration with assignment
7. **07_multiple_scalars.gms** - Multiple scalar declarations
8. **08_assignment_indexed.gms** - Indexed assignment (expected to fail)
9. **09_model_with_list.gms** - Model declaration with specific equation list

## Usage

These fixtures are used to verify statement-level parsing support:

```bash
# Parse all statement fixtures
for f in tests/fixtures/statements/*.gms; do 
    python -m src.cli parse "$f"
done
```

## Expected Results

- **Success:** 8/9 fixtures parse successfully
- **Expected failures:** 1/9 (fixture 08 - indexed assignments not supported)

See `expected_results.yaml` for detailed expectations.

## Status

- **Created:** Sprint 7 Day 9
- **Fixtures:** 9/9 ✓
- **Coverage:**
  - ✅ Model declarations
  - ✅ Solve statements
  - ✅ Scalar assignments
  - ✅ Multiple scalar declarations
  - ⚠️ Display statements (skipped, not implemented)
  - ⚠️ Option statements (not yet supported)
  - ❌ Indexed assignments (not supported)

## Notes

Statement-level features are essential for GAMS model structure. These fixtures provide regression testing and documentation of supported patterns.

### Future Enhancements

- Add support for `option` statements (currently commented out in fixture 04)
- Add support for indexed assignments (currently fails in fixture 08)
- Add loop statements (`loop(i, ...)`)
- Add file I/O statements (`put`, `execute`)
