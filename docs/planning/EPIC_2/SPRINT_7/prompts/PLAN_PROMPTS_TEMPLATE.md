# Sprint Plan Prompts Template

This template should be used to create comprehensive day-by-day execution prompts for any sprint. Copy this template and customize it with your sprint-specific information.

---

## Template Instructions

For each day of the sprint, create a prompt using this structure:

### Required Information to Extract from PLAN.md:
- Day number and title
- Objective
- Prerequisites (from KNOWN_UNKNOWNS.md, research docs, etc.)
- Tasks with time estimates
- Deliverables
- Effort estimate
- Success criteria or Checkpoint criteria
- Reference document line numbers

### Prompt Template Structure:

```markdown
## Day N Prompt: [Day Title]

**Branch:** Create a new branch named `sprint[X]-day[N]-[short-description]` from `main`

**Objective:** [Copy from PLAN.md]

**Prerequisites:**
- Read `[path/to/prerequisite/doc1.md]` - [Brief description]
- Review `[path/to/prerequisite/doc2.md]` - [Brief description]
- [Add any other prerequisites specific to this day]

**Tasks to Complete ([X-Y] hours):**

1. **[Task Name]** ([X-Y] hours)
   - [Subtask with details]
   - [Subtask with details]
   - [Subtask with details]

2. **[Task Name]** ([X-Y] hours)
   - [Subtask with details]
   - [Subtask with details]

[Continue for all tasks...]

**Deliverables:**
- [Deliverable 1]
- [Deliverable 2]
- [Continue for all deliverables...]

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
  - [ ] [Continue for all criteria...]
- [ ] Mark Day N as complete in `docs/planning/EPIC_[X]/SPRINT_[Y]/PLAN.md`
- [ ] Check off Day N in `README.md`
- [ ] Log progress to `CHANGELOG.md`
[If this is a checkpoint day:]
- [ ] Check off all Checkpoint [N] criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint [X] Day [N]: [Day Title]" \
                --body "Completes Day [N] tasks from Sprint [X] PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_[X]/SPRINT_[Y]/PLAN.md` (lines [XXX-YYY])
- [Additional reference docs specific to this day]

---
```

---

## Complete Template Usage Example

Here's how to use this template to generate prompts for a new sprint:

### Step 1: Gather Information

From your `PLAN.md`, identify:
- Sprint number (e.g., Sprint 8)
- Epic number (e.g., Epic 2)
- Number of days in the sprint (e.g., 11 days, Day 0-10)
- All prerequisite documents
- Daily tasks, objectives, and success criteria

### Step 2: Create the File Structure

Create a file at: `docs/planning/EPIC_[X]/SPRINT_[Y]/prompts/PLAN_PROMPTS.md`

### Step 3: Add Header

```markdown
# Sprint [X] Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint [X] (Days 0-[N]). Each prompt is designed to be used when starting work on that specific day.

---
```

### Step 4: Generate Each Day's Prompt

For each day (0 through N):
1. Copy the template structure above
2. Replace all placeholders:
   - `[X]` = Sprint number
   - `[Y]` = Epic number (if applicable)
   - `[N]` = Day number
   - `[Day Title]` = Actual day title from PLAN.md
   - `[short-description]` = Kebab-case brief description for branch name
   - `[X-Y]` hours = Time estimates from PLAN.md
   - `[Criterion N]` = Actual success criteria from PLAN.md
   - `[XXX-YYY]` = Line numbers in PLAN.md for this day
3. Fill in all tasks, deliverables, and prerequisites
4. Adjust quality checks if needed (some days may not need code changes)

### Step 5: Add Usage Instructions Section

```markdown
---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, README.md, and CHANGELOG.md
   - Create PR and request Copilot review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

---

## Notes

- Each prompt is designed to be self-contained
- Prerequisites ensure you have necessary context
- Quality checks ensure code quality throughout
- Completion criteria provide clear definition of "done"
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
```

---

## Automated Generation Prompt

If you want to automate the generation of PLAN_PROMPTS.md, you can use this prompt:

```
For Sprint [X] in Epic [Y], create comprehensive day-by-day execution prompts in docs/planning/EPIC_[Y]/SPRINT_[X]/prompts/PLAN_PROMPTS.md.

Read docs/planning/EPIC_[Y]/SPRINT_[X]/PLAN.md and extract complete details for each day (Day 0 through Day [N]). For each day, create a prompt that includes:

1. **Branch naming:** sprint[X]-day[N]-[short-description]
2. **Objective:** From PLAN.md
3. **Prerequisites:** 
   - Reference to KNOWN_UNKNOWNS.md (specific unknowns)
   - Reference to PREP_PLAN.md (if applicable)
   - Reference to research docs (e.g., docs/research/*.md)
   - Reference to testing strategy docs
4. **Tasks:** With time estimates from PLAN.md
5. **Deliverables:** From PLAN.md
6. **Quality Checks:** 
   - make typecheck
   - make lint
   - make format
   - make test
   - Note about skipping for docs-only commits
7. **Completion Criteria:**
   - Success criteria from PLAN.md
   - Mark day complete in PLAN.md
   - Check off in README.md
   - Log to CHANGELOG.md
   - If checkpoint day: Check off checkpoint criteria
8. **Pull Request & Review:**
   - Create PR with gh CLI
   - Request Copilot review
   - Wait for review completion
   - Address comments
   - Merge when approved
9. **Reference Documents:** With line numbers from PLAN.md

Use the template structure from docs/planning/EPIC_2/SPRINT_7/prompts/PLAN_PROMPTS_TEMPLATE.md.

Ensure each prompt is self-contained and includes all necessary context from prerequisite documents.
```

---

## Checklist for Creating PLAN_PROMPTS.md

Use this checklist when creating prompts for a new sprint:

- [ ] Identify sprint number, epic number, and number of days
- [ ] Read PLAN.md thoroughly to understand all days
- [ ] Identify all prerequisite documents (KNOWN_UNKNOWNS, research docs, etc.)
- [ ] Create prompts directory: `docs/planning/EPIC_[X]/SPRINT_[Y]/prompts/`
- [ ] Create PLAN_PROMPTS.md file
- [ ] Add header and introduction
- [ ] For each day (0 through N):
  - [ ] Copy template structure
  - [ ] Fill in branch name (sprint[X]-day[N]-[description])
  - [ ] Copy objective from PLAN.md
  - [ ] List all prerequisites with descriptions
  - [ ] List all tasks with time estimates
  - [ ] List all deliverables
  - [ ] Copy/adapt quality checks
  - [ ] List all success/checkpoint criteria
  - [ ] Add PR & Review workflow
  - [ ] Add reference document line numbers
- [ ] Add Usage Instructions section
- [ ] Add Notes section
- [ ] Review for consistency across all days
- [ ] Verify all line number references are correct
- [ ] Test one prompt to ensure it's clear and complete
- [ ] Commit and push to sprint branch

---

## Best Practices

1. **Be Specific:** Include exact file paths, function names, and commands
2. **Include Context:** Reference line numbers and prerequisite documents
3. **Time Estimates:** Copy from PLAN.md but ensure they're realistic
4. **Branch Naming:** Use consistent pattern: `sprint[X]-day[N]-[description]`
5. **Quality Checks:** Always include for code changes, note exception for docs
6. **Completion Criteria:** Make them specific and measurable
7. **PR Titles:** Use format "Sprint [X] Day [N]: [Day Title]"
8. **Prerequisites:** Include all necessary reading material
9. **Self-Contained:** Each prompt should have everything needed for that day
10. **Checkpoint Days:** Include checkpoint criteria verification

---

## Common Prerequisites to Include

Depending on the sprint, you may need to reference:

- `docs/planning/EPIC_[X]/SPRINT_[Y]/PLAN.md`
- `docs/planning/EPIC_[X]/SPRINT_[Y]/PREP_PLAN.md`
- `docs/planning/EPIC_[X]/SPRINT_[Y]/KNOWN_UNKNOWNS.md`
- `docs/research/[feature_name].md`
- `docs/testing/[strategy_name].md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/architecture/DATA_STRUCTURES.md`
- Specific GAMSLib models in `data/gamslib/`
- Previous sprint retrospectives
- Design documents

---

## Example Branch Naming Conventions

- `sprint7-day0-setup`
- `sprint7-day1-preprocessor-part1`
- `sprint7-day2-preprocessor-part2-ranges-part1`
- `sprint7-day3-set-ranges-part2`
- `sprint7-day4-integration-quick-wins`
- `sprint7-day5-gamslib-checkpoint1`
- `sprint7-day6-pytest-xdist`
- `sprint7-day7-test-optimization-checkpoint2`
- `sprint7-day8-line-numbers-multidim`
- `sprint7-day9-ci-automation-checkpoint3`
- `sprint7-day10-release-checkpoint4`

Keep branch names:
- Lowercase
- Kebab-case (hyphens)
- Descriptive but concise
- Including day number for easy tracking

---

## Tips for Writing Clear Prompts

1. **Start with context:** Explain what was done in previous days
2. **Be explicit:** Don't assume knowledge - spell out file paths, commands
3. **Include examples:** When helpful, show example code or commands
4. **Time box tasks:** Help the developer stay on track with time estimates
5. **Define "done":** Make success criteria measurable and specific
6. **Link everything:** Reference line numbers, files, and related documents
7. **Anticipate questions:** Answer common questions in prerequisites
8. **Test readability:** Would someone new to the project understand?
9. **Include recovery steps:** What to do if something goes wrong
10. **Update as needed:** If prompts are unclear during execution, improve them

---

This template should help you create comprehensive, clear, and actionable day-by-day prompts for any future sprint!
