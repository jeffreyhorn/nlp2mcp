# Incremental Documentation Guide

**Date:** 2025-11-26  
**Purpose:** Enable real-time sprint documentation via incremental SPRINT_LOG.md updates  
**Time Commitment:** 5-10 minutes per PR merge

---

## Why Incremental Documentation?

### Problem: End-of-Sprint Documentation Burden

Sprint 10 concentrated documentation on Day 10:
- ❌ Large time investment at sprint end (2-3 hours)
- ❌ Decisions documented weeks after made (details forgotten)
- ❌ No real-time progress visibility
- ❌ Retrospective pain: "What did we do on Day 3 again?"

### Solution: Update SPRINT_LOG.md After Each PR

- ✅ **Reduces Day 10 burden:** 5-10 min/PR × 8 PRs = 40-80 min total (distributed)
- ✅ **Captures decisions while fresh:** Document within hours, not weeks
- ✅ **Real-time progress tracking:** Stakeholders see progress daily
- ✅ **Easier retrospectives:** Complete timeline already documented

---

## When to Update SPRINT_LOG.md

### Trigger: **After Every PR Merge**

**Timing:** Immediately after PR merge (before starting next task)

**Exceptions:**
- ❌ Prep phase PRs (documentation, planning) → Document in PREP_PLAN.md instead
- ❌ Hotfix PRs (<10 lines, no feature work) → Optional (use judgment)
- ❌ Dependency updates (Dependabot, package bumps) → Skip

**Enforcement:** PR checklist + reviewer validation (see PR Template section)

---

## What to Document

### Required Content (Every PR)

Document in the appropriate **Daily Section** of SPRINT_LOG.md:

#### 1. **PR Number and Title**
```markdown
### PR #XXX: Feature Name

**Status:** ✅ MERGED | ⏳ IN PROGRESS | ❌ BLOCKED  
**Day:** X  
**Time Spent:** Xh (actual)  
**Parse Rate Impact:** XX% → YY% (if applicable)
```

#### 2. **Description** (2-3 sentences)
What was implemented and why:
```markdown
**Description:**
Implemented [feature name] to unlock [target model/capability]. [One sentence on technical approach].
```

#### 3. **Key Decisions** (bullet list, 1-3 items)
Important technical or design choices:
```markdown
**Key Decisions:**
- Chose approach X over Y because [reason]
- Deferred Z to Sprint 12 due to [constraint]
- Added [component] for [benefit]
```

#### 4. **Challenges** (optional, if any)
Blockers, bugs, or unexpected complexity:
```markdown
**Challenges:**
- [Challenge description] → Solved by [solution]
```

#### 5. **Metrics** (if feature unlocked model or improved performance)
```markdown
**Metrics:**
- Models unlocked: X (model names)
- Parse rate: XX% → YY%
- Test coverage: +X tests
```

### Optional Content (Use Judgment)

- **Code Examples:** Small snippets showing key changes (2-5 lines)
- **Test Coverage:** Specific test files added
- **Dependencies:** New packages or tools required
- **Follow-up Work:** Known limitations or future enhancements

---

## How to Update SPRINT_LOG.md

### Step-by-Step Process

**⏱️ Time Estimate:** 5-10 minutes

1. **Open SPRINT_LOG.md** in your editor
   ```bash
   code docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md
   ```

2. **Find the current day section**
   - Navigate to `## Day X` (e.g., `## Day 3`)
   - If day section doesn't exist, create it using the template

3. **Add PR entry** under the day section
   - Copy the PR entry template (see Templates section below)
   - Fill in PR number, title, description, key decisions
   - Add metrics if applicable

4. **Update Parse Rate Progression table** (if parse rate changed)
   - Add row to table at top of document
   - Format: `| Day X | YY% | Z/10 | Event description |`

5. **Save and commit** with SPRINT_LOG update
   ```bash
   git add docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md
   git commit -m "Update SPRINT_LOG.md: Document PR #XXX"
   git push
   ```

6. **Done!** Resume next task

---

## Templates

### Template 1: Feature Implementation PR

```markdown
### PR #XXX: [Feature Name]

**Status:** ✅ MERGED  
**Day:** X  
**Time Spent:** Xh  
**Parse Rate Impact:** XX% → YY%

**Description:**
Implemented [feature name] to unlock [target model]. [Technical approach summary in 1-2 sentences].

**Key Decisions:**
- [Decision 1 with reasoning]
- [Decision 2 with reasoning]

**Challenges:**
- [Challenge] → Solved by [solution]

**Metrics:**
- Models unlocked: X ([model names])
- Parse rate: XX% → YY%
- Test coverage: +X tests ([test file names])
```

### Template 2: Bug Fix PR

```markdown
### PR #XXX: Fix [Bug Name]

**Status:** ✅ MERGED  
**Day:** X  
**Time Spent:** Xh

**Description:**
Fixed [bug description] that prevented [capability]. Root cause was [explanation].

**Key Decisions:**
- [Fix approach chosen and why]

**Metrics:**
- Tests added: X ([test file names])
- Regressions prevented: [description]
```

### Template 3: Refactoring/Tech Debt PR

```markdown
### PR #XXX: Refactor [Component]

**Status:** ✅ MERGED  
**Day:** X  
**Time Spent:** Xh

**Description:**
Refactored [component] to improve [maintainability/performance/testability]. [Approach summary].

**Key Decisions:**
- [Refactoring approach chosen]
- [Trade-offs considered]

**Impact:**
- Code quality: [metric improvement]
- Performance: [if applicable]
- Technical debt: Resolved [issue]
```

---

## Examples: Good vs. Bad

### ❌ BAD Example (Too Vague)

```markdown
### PR #285: Dashboard stuff

Fixed some bugs and added features.

**Key Decisions:**
- Made it work better
```

**Problems:**
- No PR number context
- No time spent or metrics
- Vague description ("stuff", "some bugs")
- Key decisions not informative ("made it work better")
- Missing challenges, metrics, impact

### ✅ GOOD Example (Informative)

```markdown
### PR #285: Dashboard Performance Optimization

**Status:** ✅ MERGED  
**Day:** 9  
**Time Spent:** 4h (estimated 3h)  
**Parse Rate Impact:** No change (optimization only)

**Description:**
Optimized dashboard rendering to reduce load time from 2.3s to 0.8s (65% improvement). Implemented virtualized lists for large datasets and memoized expensive calculations.

**Key Decisions:**
- Chose `react-window` for virtualization (vs. `react-virtualized`) due to smaller bundle size
- Memoized parse result calculations using `useMemo` (recalculated on every render before)
- Deferred chart rendering to Sprint 12 (complexity 7/10, diminishing returns)

**Challenges:**
- Initial approach (pagination) showed UI flicker → Switched to virtualization
- Bundle size increased 12KB → Acceptable trade-off for performance gain

**Metrics:**
- Load time: 2.3s → 0.8s (65% improvement)
- Bundle size: +12KB (acceptable)
- Test coverage: +8 tests (dashboard_performance.test.ts)
```

**Why Good:**
- ✅ Complete metadata (day, time, impact)
- ✅ Specific description with metrics (2.3s → 0.8s)
- ✅ Detailed key decisions with rationale
- ✅ Challenges documented with solutions
- ✅ Quantifiable metrics

---

## Enforcement Strategy

### 1. PR Checklist (Required)

Every PR must include:
```markdown
- [ ] Updated SPRINT_LOG.md with PR entry
- [ ] Documented key decisions in SPRINT_LOG.md
- [ ] Updated parse rate table (if applicable)
```

**Location:** `.github/pull_request_template.md`

### 2. Reviewer Validation (Required)

**Reviewer checklist:**
1. ✅ Verify SPRINT_LOG.md updated
2. ✅ Entry contains required content (description, key decisions)
3. ✅ Metrics accurate (if applicable)
4. ✅ No merge until SPRINT_LOG.md updated

**Process:**
- If SPRINT_LOG.md not updated → Request changes: "Please update SPRINT_LOG.md per incremental documentation guide"
- If entry too vague → Request more detail
- If entry missing key decisions → Ask for clarification

### 3. Compliance Tracking (Optional)

Track compliance for first 5 PRs of Sprint 11:
- **Metric:** % PRs with SPRINT_LOG.md update at merge time
- **Target:** 100% (all PRs documented)
- **Measure:** Review Sprint 11 Git history after Day 5

**If Compliance Low (<80%):**
- Retrospective discussion: Is process too burdensome?
- Consider automation (pre-commit hooks, GitHub Actions)
- Adjust guidance or expectations

---

## Common Questions

### Q: What if I forget to update SPRINT_LOG.md before merging?

**A:** Add a follow-up commit immediately after merge:
```bash
# After realizing you forgot
git checkout main
git pull
# Update SPRINT_LOG.md
git add docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md
git commit -m "Update SPRINT_LOG.md: Document PR #XXX (missed in merge)"
git push
```

**Better:** Make it a habit - update SPRINT_LOG.md before marking PR ready for review.

### Q: What if the PR is tiny (1-line change)?

**A:** Use judgment:
- **Document if:** Changes parse rate, fixes bug, implements feature (even small)
- **Skip if:** Typo fix, dependency update, reformatting
- **1-line entry OK:** "PR #XXX: Fixed typo in parser error message (Day X, 5 min)"

### Q: What if multiple people work on same day?

**A:** Both add entries to same day section:
```markdown
## Day 3

### PR #100: Feature A (Author: Alice)
[Alice's entry]

### PR #101: Feature B (Author: Bob)
[Bob's entry]
```

### Q: Do I update SPRINT_LOG.md during PR or after merge?

**A:** **During PR** (before marking ready for review):
1. Implement feature
2. Write tests
3. Update SPRINT_LOG.md (as part of PR)
4. Mark PR ready for review

**Rationale:** Reviewer can validate documentation quality before merge.

### Q: What if I don't know parse rate impact yet?

**A:** Estimate or measure:
```markdown
**Parse Rate Impact:** TBD (will measure after merge)
```

Then update after merge:
```bash
# After measuring parse rate
git add docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md
git commit -m "Update SPRINT_LOG.md: Add parse rate metrics for PR #XXX"
git push
```

---

## Time Management

### Expected Time Investment

| Activity | Time | Frequency |
|----------|------|-----------|
| Update SPRINT_LOG.md per PR | 5-10 min | Per PR (8-10 PRs/sprint) |
| Update parse rate table | 2 min | Per model unlock (3-5/sprint) |
| Reviewer validation | 2 min | Per PR review |
| **Total per sprint** | **60-120 min** | **Distributed across 10 days** |

**Compare to Sprint 10:** 2-3 hours concentrated on Day 10 → 60-120 min distributed

**Net Benefit:** 
- **Time saved:** 0-60 min (amortized cost lower due to no context switching)
- **Quality improved:** Decisions documented while fresh (higher accuracy)
- **Stress reduced:** No end-of-sprint documentation crunch

---

## Success Criteria

### Sprint 11 Goals

1. ✅ **100% PR compliance:** All 8-10 PRs update SPRINT_LOG.md at merge time
2. ✅ **Quality threshold:** All entries include description + key decisions
3. ✅ **Time target:** Average ≤10 min per PR (max 120 min total)
4. ✅ **Stakeholder feedback:** Real-time progress visibility improves (qualitative)

### Measure at Sprint 11 Retrospective

- **Compliance:** % PRs with SPRINT_LOG.md update (target: 100%)
- **Quality:** % entries with all required content (target: 100%)
- **Time:** Average time per entry (target: ≤10 min)
- **Developer sentiment:** Survey team - is process helpful or burdensome?

**Decision Point:** Keep, modify, or abandon incremental documentation based on Sprint 11 results.

---

## References

- Sprint 10 Retrospective: `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` (Problem identification)
- Sprint 10 SPRINT_LOG.md: `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md` (Structure reference)
- KNOWN_UNKNOWNS.md: Unknown 5.1 (Incremental Documentation Enforcement)
