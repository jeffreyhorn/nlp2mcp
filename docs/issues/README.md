# Parser Limitations and Known Issues

This directory contains detailed documentation of parser limitations discovered during development and testing. Each issue document provides reproduction steps, technical analysis, and suggested fixes.

## Issue Index

### High Priority

1. **[Multi-Dimensional Parameter Data Not Supported](parser-multi-dimensional-parameters-not-supported.md)**
   - **Status**: Open
   - **Impact**: High - Blocks realistic problem modeling
   - **Summary**: Cannot specify 2D/3D parameter data using dotted notation (e.g., `usage(i,j) / i1.j1 2.0 /`)
   - **Workaround**: Use 1D parameters only or restructure model
   - **Affects**: Resource allocation, transportation, network flow, production planning problems

### Medium Priority

2. **[Asterisk Notation Not Supported](parser-asterisk-notation-not-supported.md)** ([#136](https://github.com/jeffreyhorn/nlp2mcp/issues/136))
   - **Status**: Open
   - **Impact**: Moderate - Forces manual expansion of large sets
   - **Summary**: Cannot use range notation like `/i1*i100/` for set element definitions
   - **Workaround**: Use explicit comma-separated lists
   - **Affects**: All large-scale models, multiple example files

3. **[Long Comma-Separated Lists Performance](parser-long-comma-separated-lists-performance.md)** ([#138](https://github.com/jeffreyhorn/nlp2mcp/issues/138))
   - **Status**: Open
   - **Impact**: Moderate - Limits practical model size
   - **Summary**: Parser performance degrades significantly with 100+ element lists (24s for 100 elements)
   - **Workaround**: Limit models to ~100 elements per set
   - **Affects**: Large-scale model testing and production use
   - **Related**: Asterisk notation would mitigate this issue

### Low Priority

4. **[Positive Variables Keyword Not Supported](parser-positive-variables-keyword-not-supported.md)**
   - **Status**: Open
   - **Impact**: Low - Excellent workaround available
   - **Summary**: Cannot use `Positive Variables` declaration keyword
   - **Workaround**: Use explicit constraints `x =g= 0` (mathematically equivalent)
   - **Affects**: GAMS compatibility, several example files

5. **[Hyphens in Equation Descriptions](parser-hyphens-in-equation-descriptions.md)** ([#137](https://github.com/jeffreyhorn/nlp2mcp/issues/137))
   - **Status**: Open
   - **Impact**: Very Low - Cosmetic only
   - **Summary**: Equation descriptions cannot contain hyphens (e.g., "non-negativity")
   - **Workaround**: Remove hyphens or use underscores
   - **Affects**: Description text only, no semantic impact

## Issue Summary Table

| Issue | Priority | Impact | Workaround Quality | Blocks Production |
|-------|----------|--------|-------------------|-------------------|
| Multi-Dimensional Parameters | High | High | Poor | Yes |
| Asterisk Notation | Medium | Moderate | Fair | Partially |
| Long List Performance | Medium | Moderate | Fair | Partially |
| Positive Variables | Low | Low | Excellent | No |
| Hyphens in Descriptions | Low | Very Low | Excellent | No |

## Discovery Context

All these issues were discovered during **Sprint 5 Prep Task 8: Create Large Model Test Fixtures** (2025-11-06). The goal was to create realistic large-scale test models for production hardening, which revealed parser limitations when working with:

- Large sets (100+ elements)
- Multi-dimensional parameters (resource usage matrices)
- Standard GAMS syntax features

## Reproduction Environment

- **Version**: Current development branch
- **Test Files**: `tests/fixtures/large_models/`
- **Example Files**: `examples/sprint4_*.gms`

## Priority Definitions

- **High**: Blocks realistic problem types, poor workaround, required for production
- **Medium**: Limits model scale or usability, acceptable workaround available
- **Low**: Minor inconvenience, excellent workaround, cosmetic only

## Impact Assessment

### Combined Impact

The combination of **asterisk notation not supported** + **long list performance issues** creates a significant blocker for large models:

1. Cannot use `/i1*i1000/` (asterisk not supported)
2. Must write `/i1, i2, i3, ..., i1000/` (1000 elements)
3. Parser times out or takes minutes (performance issue)
4. **Result**: Cannot parse realistic large-scale models

**Recommendation**: Fix asterisk notation first (provides compact input) which will partially mitigate the performance issue since the input will be much shorter.

### Production Readiness

Current parser limitations prevent these problem types:

- ❌ **Resource Allocation**: Requires 2D parameter data
- ❌ **Transportation**: Requires 2D cost matrices  
- ❌ **Network Flow**: Requires 2D incidence matrices
- ❌ **Large-Scale Models**: Performance limits at ~100 elements
- ✓ **Small-Scale Problems**: Works well for models with <100 elements and 1D parameters

## Suggested Fix Order

1. **Asterisk Notation** (Medium priority, high value)
   - Enables compact representation of large sets
   - Unblocks several example files
   - Partially mitigates performance issue

2. **Multi-Dimensional Parameters** (High priority)
   - Critical for realistic problems
   - Enables resource allocation, transportation, network flow
   - No good workaround

3. **Performance Optimization** (Medium priority)
   - Necessary for large-scale models
   - Benefits all parsing operations
   - May be partially addressed by asterisk notation

4. **Positive Variables** (Low priority)
   - Nice-to-have for compatibility
   - Excellent workaround exists
   - Low user friction

5. **Hyphens in Descriptions** (Low priority)
   - Purely cosmetic
   - Trivial workaround
   - Fix only if doing broader description work

## Testing Coverage

Each issue document includes:
- Minimal reproduction test case
- Expected vs actual behavior
- Technical analysis
- Suggested fixes
- Test requirements for verification

These can be converted directly into:
- Unit tests for parser behavior
- Integration tests for end-to-end functionality
- Performance regression tests
- GitHub issues for tracking

## Contributing

When creating GitHub issues from these documents:

1. Copy the issue document as the issue description
2. Add labels: `parser`, `bug`, priority level (`high`, `medium`, `low`)
3. Reference the document: "See docs/issues/[filename].md for full details"
4. Link related issues (e.g., asterisk notation + performance)
5. Add to appropriate project board/milestone

## References

- **Sprint 5 Prep Plan**: `docs/planning/SPRINT_5/PREP_PLAN.md`
- **Test Models**: `tests/fixtures/large_models/`
- **Example Files**: `examples/sprint4_*.gms`
- **CHANGELOG**: Entry for Sprint 5 Prep Task 8
