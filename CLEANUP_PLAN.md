# Repository Cleanup Plan

**Branch:** `cleanup-docs-structure`  
**Date:** October 31, 2025  
**Purpose:** Improve repository organization and remove clutter

---

## Issues Identified

### 1. Root Directory Clutter
- `inspect_simple_nlp.py` - Development script in root
- `simple_nlp_mcp.lst` - GAMS output file (build artifact)
- `AGENTS.md` - Claude agent guidelines (not project documentation)
- `setup.py` - Potentially redundant with `pyproject.toml`

### 2. Docs Organization
- Loose AD-related docs at `docs/` root level
- Should be organized into subdirectories
- Some overlap between `ad_architecture.md` and `ad_design.md`

### 3. Build Artifacts
- `.coverage` file in root
- `htmlcov/` directory
- These should be git-ignored and cleaned

---

## Cleanup Actions

### Phase 1: Root Directory Cleanup

#### Action 1.1: Move Development Scripts
```bash
# Move inspect script to scripts/
mv inspect_simple_nlp.py scripts/inspect_simple_nlp.py
```
**Rationale:** Keep root directory clean, scripts belong in `scripts/`

#### Action 1.2: Remove Build Artifacts
```bash
# Remove GAMS output file
rm simple_nlp_mcp.lst

# Remove coverage files (will be regenerated)
rm .coverage
rm -rf htmlcov/
```
**Rationale:** These are generated files, not source code

#### Action 1.3: Update .gitignore
Add to `.gitignore`:
```
# GAMS output files
*.lst

# Coverage reports
.coverage
htmlcov/
```
**Rationale:** Prevent build artifacts from being committed

#### Action 1.4: Handle AGENTS.md
**Options:**
- A) Move to `docs/development/AGENTS.md`
- B) Remove (if it's just Claude-specific instructions)
- C) Rename to `CONTRIBUTING.md` if it's contributor guidelines

**Decision:** Move to `docs/development/AGENTS.md` for now

#### Action 1.5: Handle setup.py
**Check if redundant:**
- If `pyproject.toml` has all setup info → Remove `setup.py`
- If still needed → Keep it

**Decision:** Check first, likely remove

---

### Phase 2: Docs Directory Reorganization

#### Action 2.1: Create docs/ad/ Directory
```bash
mkdir -p docs/ad
```

#### Action 2.2: Move AD Documentation
```bash
# Move loose AD docs into organized structure
mv docs/ad_architecture.md docs/ad/ARCHITECTURE.md
mv docs/ad_design.md docs/ad/DESIGN.md
mv docs/derivative_rules.md docs/ad/DERIVATIVE_RULES.md
```
**Rationale:** Group related documentation together

#### Action 2.3: Consider Consolidation
- `ad_architecture.md` and `ad_design.md` have significant overlap
- **Recommendation:** Merge into single `docs/ad/README.md` or keep separate?
- **Decision:** Keep separate for now, but note in README they're related

#### Action 2.4: Create docs/ad/README.md
Add index file to guide readers:
```markdown
# Automatic Differentiation Documentation

This directory contains documentation for the AD (Automatic Differentiation) module.

## Files

- **ARCHITECTURE.md** - High-level architectural decisions and design rationale
- **DESIGN.md** - Detailed design and implementation approach
- **DERIVATIVE_RULES.md** - Complete reference of all derivative rules implemented

## Quick Start

1. Start with ARCHITECTURE.md for the big picture
2. Read DESIGN.md for implementation details
3. Reference DERIVATIVE_RULES.md for specific derivative formulas
```

---

### Phase 3: Clean Up Planning Documents

#### Action 3.1: Archive Draft Plans
```bash
# Move all DRAFT_PLANS to archive subdirectory
mkdir -p docs/planning/SPRINT_2/archive
mv docs/planning/SPRINT_2/DRAFT_PLANS/* docs/planning/SPRINT_2/archive/
rmdir docs/planning/SPRINT_2/DRAFT_PLANS

mkdir -p docs/planning/SPRINT_3/archive
mv docs/planning/SPRINT_3/DRAFT_PLANS/* docs/planning/SPRINT_3/archive/
rmdir docs/planning/SPRINT_3/DRAFT_PLANS
```
**Rationale:** Drafts are historical, should be archived not prominent

#### Action 3.2: Add Planning README
Create `docs/planning/README.md`:
```markdown
# Sprint Planning Documentation

## Current Sprint
- Sprint 3: ✅ COMPLETE
- Sprint 4: 🔄 PREP PHASE

## Sprint Summaries
- [Sprint 1 Summary](SPRINT_1/SUMMARY.md)
- [Sprint 2 Summary](SPRINT_2/SUMMARY.md)
- [Sprint 3 Summary](SPRINT_3/SUMMARY.md)

## Sprint Retrospectives
- [Sprint 2 Retrospective](SPRINT_2/RETROSPECTIVE.md)
- [Sprint 3 Retrospective](SPRINT_3/RETROSPECTIVE.md)

## Project Plan
- [Overall Project Plan](PROJECT_PLAN.md) - 5-sprint roadmap

## Archive
Each sprint folder contains an `archive/` subdirectory with draft plans and working documents.
```

---

### Phase 4: Update Documentation References

#### Action 4.1: Update README.md
Update any references to moved files:
- `ad_architecture.md` → `docs/ad/ARCHITECTURE.md`
- `ad_design.md` → `docs/ad/DESIGN.md`
- `derivative_rules.md` → `docs/ad/DERIVATIVE_RULES.md`

#### Action 4.2: Update AGENTS.md References (if keeping)
Update path references if file moved

#### Action 4.3: Update Sprint Planning Docs
Update any internal links to draft plans to point to archive

---

## Execution Order

1. ✅ Create this cleanup plan
2. [ ] Phase 1: Root directory cleanup (Actions 1.1-1.5)
3. [ ] Phase 2: Docs reorganization (Actions 2.1-2.4)
4. [ ] Phase 3: Planning docs cleanup (Actions 3.1-3.2)
5. [ ] Phase 4: Update references (Actions 4.1-4.3)
6. [ ] Verify all tests still pass
7. [ ] Commit and push

---

## Verification Checklist

After cleanup, verify:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] No broken links in documentation
- [ ] README.md still accurate
- [ ] Project structure clean and organized
- [ ] `.gitignore` updated appropriately
- [ ] No accidental deletions of important files

---

## Rollback Plan

If issues arise:
```bash
# This branch can be abandoned, main is unaffected
git checkout main
git branch -D cleanup-docs-structure
```

---

## Benefits

After cleanup:
1. **Cleaner root directory** - Only essential files visible
2. **Better organized docs** - Related docs grouped together
3. **No build artifacts** - Clean git status
4. **Easier navigation** - Clear structure with README files
5. **Professional appearance** - Ready for external contributors

---

**Status:** Draft - Ready for execution  
**Estimated Time:** 30-45 minutes  
**Risk Level:** Low (working on separate branch)
