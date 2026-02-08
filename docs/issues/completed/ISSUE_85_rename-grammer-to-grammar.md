# Rename `gams_grammer.lark` to `gams_grammar.lark`

**Status**: Open  
**Priority**: Low  
**Component**: Parser / Grammar  
**Discovered**: Sprint 4 Checkpoint 1 PR Review  
**GitHub Issue**: #85  
**Type**: Refactoring / Technical Debt  

## Summary

The file `src/gams/gams_grammer.lark` has a spelling error in its filename. The word "grammar" is misspelled as "grammer". This should be corrected to improve code professionalism and prevent confusion.

## Problem

**Current filename**: `src/gams/gams_grammer.lark`  
**Correct filename**: `src/gams/gams_grammar.lark`

The misspelling appears in:
1. The actual file name on disk
2. All import statements that reference this file
3. Documentation and comments that reference the file

## Impact

**Severity**: Low - This is purely cosmetic and does not affect functionality.

**Benefits of fixing**:
- Improved code professionalism
- Prevents confusion for new contributors
- Corrects spelling in documentation
- Sets good precedent for code quality

## Discovered During

PR review for Sprint 4 Checkpoint 1. A reviewer suggested correcting the spelling in `docs/planning/EPIC_1/SPRINT_4/CHECKPOINT1.md` line 59, but the documentation correctly reflects the actual (misspelled) filename.

## Required Changes

### 1. Rename the file
```bash
git mv src/gams/gams_grammer.lark src/gams/gams_grammar.lark
```

### 2. Update all Python imports and references

Search for all references to `gams_grammer` and update to `gams_grammar`:

```bash
# Find all references
grep -r "gams_grammer" --include="*.py" --include="*.md" .
```

Expected files to update:
- Any Python files that import or reference the grammar file
- Test files that reference the grammar
- Documentation files (README.md, CHANGELOG.md, planning docs)
- Configuration files if applicable

### 3. Update documentation references

Files likely to reference the grammar file:
- `README.md`
- `CHANGELOG.md`
- `docs/planning/EPIC_1/SPRINT_4/CHECKPOINT1.md`
- `docs/planning/EPIC_1/SPRINT_4/PLAN.md`
- Any other planning or design documents

### 4. Search for variable/constant names

Check for any variables or constants that might include "grammer":
```bash
grep -r "grammer" --include="*.py" .
```

## Implementation Steps

1. **Search Phase**:
   - Run comprehensive grep to find all occurrences of "grammer"
   - Document all files that need updates
   - Verify no dynamically constructed paths use the old name

2. **Rename Phase**:
   - Use `git mv` to rename the file (preserves history)
   - Update all import statements
   - Update all string literals referencing the file
   - Update all documentation

3. **Verification Phase**:
   - Run all tests: `make test`
   - Run type checking: `make typecheck`
   - Run linting: `make lint`
   - Grep for any remaining "grammer" references
   - Verify documentation builds correctly

4. **Commit**:
   - Single atomic commit with descriptive message
   - Include all file renames and reference updates

## Acceptance Criteria

- [ ] File renamed from `gams_grammer.lark` to `gams_grammar.lark`
- [ ] All Python imports updated
- [ ] All string literal references updated
- [ ] All documentation references updated
- [ ] All tests passing (754 tests, 100%)
- [ ] No mypy errors
- [ ] No ruff errors
- [ ] Zero grep results for "grammer" (except this issue file)
- [ ] Git history preserved through `git mv`

## Estimated Effort

**Time**: 30 minutes - 1 hour

**Complexity**: Low - Straightforward find-and-replace operation

## Priority Justification

**Priority: Low** because:
- No functional impact
- Not blocking any features
- Can be done at any time
- Good "quick win" task for a cleanup sprint

**Good candidate for**:
- Cleanup day task
- Onboarding task for new contributors
- Between-sprint maintenance work

## Notes

- This is a good example of why automated tooling (like IDE spell checkers) should be used during development
- Consider adding a spell-check linter to the CI/CD pipeline to catch such issues early
- The misspelling has persisted through multiple sprints, suggesting it was in the initial project setup

## Related Files

Files that definitely reference the grammar file:
- `src/gams/gams_grammer.lark` (the file itself)
- `src/ir/parser.py` (likely imports the grammar)
- `tests/gams/test_parser.py` (likely tests grammar parsing)
- `docs/planning/EPIC_1/SPRINT_4/CHECKPOINT1.md` (line 59)

## Resolution

When this issue is resolved:
1. Move this file to `docs/issues/completed/rename-grammer-to-grammar.md`
2. Update status to "Resolved"
3. Add resolution date and commit hash
4. Update any tracking documents
