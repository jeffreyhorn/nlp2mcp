# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

**Type:**
<!-- Check one -->
- [ ] Feature implementation
- [ ] Bug fix
- [ ] Refactoring
- [ ] Documentation
- [ ] Testing
- [ ] Other: ___________

**Related Issue/Task:**
<!-- Link to issue, prep task, or sprint task -->
- Closes #
- Related to Task: ___________

## Changes

<!-- List the main changes made in this PR -->

### Files Modified
<!-- List key files changed -->
- 
- 
- 

### Key Decisions
<!-- Document important technical or design choices -->
- 
- 

## Testing

<!-- Describe testing performed -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All tests passing locally

**Test Coverage:**
<!-- List test files added/modified -->
- 

## Impact

**Parse Rate Impact:**
<!-- If feature unlocks models or changes parse rate -->
- Before: ___%
- After: ___%
- Models unlocked: ___________

**Performance Impact:**
<!-- If applicable -->
- No performance impact
- Performance improved: ___________
- Performance regression: ___________ (justified by: ___________)

## Documentation

**Sprint Documentation (Required for non-prep PRs):**
- [ ] Updated SPRINT_LOG.md with PR entry (see [Incremental Documentation Guide](../docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md))
- [ ] Documented key decisions in SPRINT_LOG.md
- [ ] Updated parse rate table (if applicable)

**Code Documentation:**
- [ ] Added/updated docstrings for new functions
- [ ] Added/updated comments for complex logic
- [ ] Updated README.md (if user-facing changes)

**Why This Matters:**
Sprint 10 Retrospective identified incremental documentation as key improvement. Updating SPRINT_LOG.md after each PR:
- ✅ Reduces Day 10 burden (5-10 min/PR vs 2-3 hours at end)
- ✅ Captures decisions while fresh
- ✅ Enables real-time progress tracking

## Checklist

**Before Marking Ready for Review:**
- [ ] Code follows project style guidelines
- [ ] All tests passing (`make test`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Linting passes (`make lint`)
- [ ] Code formatted (`make format`)
- [ ] SPRINT_LOG.md updated (required for non-prep PRs)
- [ ] No commented-out code or debug prints
- [ ] No breaking changes (or documented in PR description)

**Reviewer Checklist:**
- [ ] Code review completed
- [ ] Tests adequate and passing
- [ ] SPRINT_LOG.md entry verified (description + key decisions present)
- [ ] Documentation sufficient
- [ ] No obvious performance or security issues

## Additional Notes

<!-- Any additional context, screenshots, or information for reviewers -->
