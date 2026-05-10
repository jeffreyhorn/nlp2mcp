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

## CI Workflow Changes

<!-- Complete this section ONLY if modifying files in .github/workflows/ -->

**If this PR modifies CI workflows:**
- [ ] Workflow syntax validated locally (`yamllint .github/workflows/`)
- [ ] Actions validated with actionlint (`actionlint`)
- [ ] File paths verified (all referenced files exist)
- [ ] Matrix builds tested locally (if applicable)
- [ ] Secrets/permissions documented (if new ones added)
- [ ] CI passes on PR before merge

**See:** [CI Workflow Testing Guide](../docs/infrastructure/CI_WORKFLOW_TESTING.md)

## Emit-Affecting Changes (PR14)

<!-- Complete this section ONLY if modifying files under src/emit/, src/kkt/stationarity.py,
     src/kkt/complementarity.py, src/ad/derivative_rules.py, src/ad/constraint_jacobian.py.
     Per CONTRIBUTING.md §"Emit-Affecting PRs" — codified per Sprint 25 retrospective PR14. -->

**If this PR modifies emit-affecting files:**
- [ ] At least one regenerated `data/gamslib/mcp/<model>_mcp.gms` file is included in the diff
- [ ] PR description identifies the affected model(s) and which `_mcp.gms` section reviewers should read
- [ ] Reviewer has read the relevant section of the regenerated `_mcp.gms` (variable bounds / init group + affected equation block(s))
- [ ] No clobber patterns observed (duplicate assignments, misordered clamps — see CONTRIBUTING.md for examples)

**Refactor-only exception (`byte-stable-refactor` label):**
- [ ] PR is byte-diff-verified to produce zero changes in emitted `_mcp.gms` files across all currently-translating models
- [ ] PR description includes the byte-diff verification command + result (e.g., `diff -r /tmp/pre /tmp/post` → 0 diffs across N models, `PYTHONHASHSEED=0`)
- [ ] `byte-stable-refactor` label applied

**See:** [CONTRIBUTING.md §"Emit-Affecting PRs"](../CONTRIBUTING.md#emit-affecting-prs--required-gms-artifact-in-diff-pr14)

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
- [ ] CI workflow changes validated (if applicable)

## Additional Notes

<!-- Any additional context, screenshots, or information for reviewers -->
