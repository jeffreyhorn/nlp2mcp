# Issue Tracking

This directory contains detailed issue descriptions suitable for GitHub Issues or other tracking systems.

## Active Issues

### Critical Priority

None currently.

### High Priority

1. **[KKT Assembly Bug: Equality Multipliers Missing](./kkt-assembly-missing-equality-multipliers.md)**
   - **Status**: Open
   - **Affects**: Min/max reformulation, fixed variables
   - **Impact**: Prevents these features from generating valid MCP models
   - **Effort**: High (requires deep investigation of KKT assembly logic)

### Medium Priority

2. **[PATH Solver Infeasibility on Nonlinear Models](./path-solver-infeasible-nonlinear-models.md)**
   - **Status**: Open - Investigation Required
   - **Affects**: bounds_nlp, nonlinear_mix test cases
   - **Impact**: 40% of test cases fail with Model Status 5
   - **Effort**: Medium (requires investigation and potential reformulation)

### Low Priority

3. **[Power Operator Syntax Support](./power-operator-syntax-support.md)**
   - **Status**: Open - Enhancement
   - **Affects**: User convenience
   - **Impact**: Users must use `power(x,2)` instead of `x**2`
   - **Effort**: Low (simple grammar update)

4. **[Smooth Abs Initialization Issues](./smooth-abs-initialization-issues.md)**
   - **Status**: Open - Enhancement
   - **Affects**: Smooth abs feature usability
   - **Impact**: Users may encounter domain errors without initialization
   - **Effort**: Low-Medium (initialization hints + documentation)

## Issue Status Legend

- **Open**: Issue identified, not yet addressed
- **In Progress**: Actively being worked on
- **Investigation Required**: Needs analysis before solution is clear
- **Blocked**: Waiting on another issue or external dependency
- **Resolved**: Fixed and verified
- **Won't Fix**: Decided not to address

## How to Use These Files

Each issue file contains:

1. **Issue Type & Priority**: Classification for triage
2. **Summary**: Brief description
3. **Reproduction Steps**: Exact steps to reproduce the problem
4. **Technical Analysis**: Deep dive into the root cause
5. **Proposed Solutions**: Multiple options with trade-offs
6. **Implementation Steps**: Concrete action items
7. **Test Cases**: What tests need to pass
8. **Acceptance Criteria**: Definition of done
9. **Workarounds**: Temporary solutions for users
10. **Related Files**: Where to look in the codebase

## Creating GitHub Issues

To create a GitHub issue from one of these files:

1. Copy the entire markdown content
2. Create new issue on GitHub
3. Paste content as issue description
4. Add appropriate labels:
   - Priority: `priority:high`, `priority:medium`, `priority:low`
   - Type: `bug`, `enhancement`, `investigation`
   - Component: `kkt`, `parser`, `path-solver`, etc.

## Priority Guidelines

- **Critical**: Blocks core functionality, affects all users
- **High**: Blocks important features, affects many users
- **Medium**: Affects specific use cases, has workarounds
- **Low**: Nice to have, cosmetic, or very rare edge cases

## Effort Estimates

- **Low**: < 4 hours, straightforward fix
- **Medium**: 1-3 days, requires some investigation
- **High**: 1+ weeks, complex changes or refactoring

## Contributing

When adding new issues:

1. Use the existing files as templates
2. Include reproduction steps
3. Provide technical analysis
4. Suggest multiple solutions with pros/cons
5. List acceptance criteria
6. Update this README

## Sprint Planning

Issues are tracked here to supplement Sprint planning documents in `docs/planning/`.

Current sprint status: SPRINT_4 - Day 8 completed
- Critical bug (sign error) resolved ✅
- PATH validation framework complete ✅
- KKT assembly bug identified (Issue #1) ⚠️
