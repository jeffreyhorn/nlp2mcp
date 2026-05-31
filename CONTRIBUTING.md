# Contributing to nlp2mcp

Thank you for your interest in contributing to nlp2mcp! This document provides essential guidelines for contributing to the project.

---

## Quick Start

**For comprehensive development guidelines, see [docs/development/AGENTS.md](docs/development/AGENTS.md)**

That document contains detailed information about:
- Complete project structure and module organization
- Detailed coding standards and conventions
- Testing practices and patterns
- Build system and development workflow
- Sprint planning process

---

## Essential Rules

### Before You Contribute

1. **Python Version**: This project requires **Python 3.12+**
   - Uses modern type hints (`dict`, `list`, `X | None`)
   - Uses `strict=` parameter on `zip()` calls
   - No `from typing import Dict, List, Optional` needed

2. **Development Setup**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   make install-dev
   ```

3. **Before Every Commit**:
   ```bash
   make format   # Auto-format with black + ruff
   make lint     # Check types and style
   make test     # Run all tests (must pass)
   ```

---

## Code Style

### Naming Conventions
- **Functions/modules**: `snake_case` (e.g., `normalize_equation`, `parse_model`)
- **Classes**: `CapWords` (e.g., `ModelIR`, `EquationDef`, `VarRef`)
- **Constants**: `UPPER_CASE` (e.g., `INF`, `WRAPPER_NODES`)
- **Private/internal**: Leading underscore `_helper_function`

### Modern Python 3.12 Type Hints
```python
# ✅ Correct (Python 3.12+)
def process(items: dict[str, int]) -> list[str] | None:
    ...

# ❌ Old style (don't use)
from typing import Dict, List, Optional
def process(items: Dict[str, int]) -> Optional[List[str]]:
    ...
```

### Required Practices
- ✅ Type hints on all public functions
- ✅ Docstrings on all public classes and functions
- ✅ `strict=True` or `strict=False` on all `zip()` calls (no bare `zip()`)
- ✅ Use `@dataclass(frozen=True)` for immutable data structures
- ✅ Line length: 100 characters (Black default)

---

## Testing Guidelines

### Test Organization
- Tests mirror source structure: `tests/ad/` for `src/ad/`, etc.
- Test files: `test_<module>.py` 
- Test functions: `test_<specific_behavior>`

### Test Requirements
- **All tests must pass**: `make test` (currently 602 tests)
- **Add tests for new features**: Maintain >85% coverage
- **Use pytest fixtures**: See existing tests for patterns
- **Parametrize variants**: Use `@pytest.mark.parametrize`

### Example Test Pattern
```python
import pytest
from src.ir.parser import parse_model_file

def test_specific_behavior():
    """Test description in plain English."""
    model = parse_model_file('examples/simple_nlp.gms')
    assert model.equations
    assert len(model.variables) > 0

@pytest.mark.parametrize("input,expected", [
    ("x", "x"),
    ("x_1", "x_1"),
])
def test_multiple_cases(input, expected):
    assert process(input) == expected
```

---

## Development Workflow

### Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or: fix/issue-description
   ```

2. **Make your changes**:
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Verify quality**:
   ```bash
   make format    # Auto-format code
   make lint      # Check types and style
   make test      # Run all tests
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "Brief description of changes
   
   - Detailed point 1
   - Detailed point 2
   
   Addresses: #issue-number (if applicable)"
   ```

5. **Push and create PR**:
   ```bash
   git push -u origin feature/your-feature-name
   # Then create Pull Request on GitHub
   ```

### CI/CD Requirements

All PRs must pass:
- ✅ All 602+ tests passing
- ✅ Type checking (mypy)
- ✅ Linting (ruff)
- ✅ Code formatting (black)

---

## Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)

**Codified per Sprint 25 retrospective recommendation PR14 (reaffirmation of Sprint 24's PR14).**

### The rule

If your PR modifies any of the following, you **MUST** include at least one regenerated `_mcp.gms` artifact from an affected model in the PR diff, and reviewers **MUST** read the relevant section of the regenerated file:

- `src/emit/**/*.py`
- `src/kkt/stationarity.py`
- `src/kkt/complementarity.py`
- `src/ad/derivative_rules.py`
- `src/ad/constraint_jacobian.py`

### Why

Sprint 25 PR #1349 introduced a per-instance `.l` override emit-ordering bug that clobbered ~120 lines of `.l = expr` overrides in `clearlak_mcp.gms`. The bug **passed all unit tests + `gams action=c` compile-only validation** and was caught only by Copilot reading the regenerated `clearlak_mcp.gms` during PR #1360 review — a 5-minute manual scan that would have caught it at the original PR #1349 merge.

Unit tests + compile validation cannot reliably detect emit-shape regressions because:
- Unit tests assert on AST/IR structure or per-token strings, not on the cross-cutting interaction of multiple emit groups.
- `gams action=c` accepts emit ordering that's syntactically valid but semantically clobbers (e.g., a `.l = expr` override followed by a bulk init `.l = default`).

The companion automated check is **PR19** (Sprint 26 Task 8 design — pre-merge solve-time validation CI). PR19 catches a different failure mode (PATH-solve-time regressions on canary models) and does **not** replace human review of the emitted `.gms`.

### Regeneration command

```bash
# Identify an affected model. Tier 0/1 canaries are usually the easiest to read:
#   dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive
# Or a Pattern C target (camcge / cesam2 / fawley / otpop) if your PR targets that work.

# Regenerate just the affected model:
mkdir -p data/gamslib/mcp
.venv/bin/python -m src.cli "data/gamslib/raw/<model>.gms" \
    -o "data/gamslib/mcp/<model>_mcp.gms" \
    --skip-convexity-check --quiet

# Or regenerate the entire pipeline (slow — ~2-3h, only if your PR has corpus-wide impact):
.venv/bin/python scripts/gamslib/run_full_test.py --quiet
```

The regenerated `data/gamslib/mcp/<model>_mcp.gms` file (or files) goes in the PR diff alongside your `src/` changes.

### What reviewers must do

1. **Read the relevant section** of the regenerated `_mcp.gms` — at minimum the variable bounds / init group + the equation block(s) your PR touches.
2. **Look for clobber patterns** — duplicate assignments where one silently overrides the other (e.g., `var.l(idx) = expr` followed by `var.l(idx) = 1.0`).
3. **Look for ordering bugs** — clamps applied AFTER explicit overrides (e.g., `v.l('h0') = 0` followed by `v.l(h) = min(max(..., 1e-6), ...)` — see #1374 rocket case).
4. **Spot-check stationarity emit shape** — for `src/kkt/stationarity.py` PRs, read the `stat_<var>` blocks for affected variables; look for spurious `Sum((...,), ...)` wraps or missing cross-terms (#1334 / #1335 patterns).

### Exception: refactor-only PRs (`byte-stable-refactor` label)

If your PR is a **pure refactor** that you have byte-diff-verified produces zero changes in the emitted `_mcp.gms` files across all currently-translating models, you may apply the **`byte-stable-refactor`** PR label to bypass this rule.

**Reviewer responsibility when the label is present:** verify the PR description includes:
- The byte-diff verification command actually run (e.g., `diff -r /tmp/pre-mcp /tmp/post-mcp`).
- The result (e.g., "0 diffs across 141 currently-translating models per `PYTHONHASHSEED=0`").
- A justification for why no `.gms` artifact is included.

The canonical Sprint 24/25 example: PR #1353's #1271 dispatcher refactor — collapsed `_loop_tree_to_gams_subst_dispatch` into `_loop_tree_to_gams(node, *, token_subst=None)`, removed ~140 LOC, byte-diff verified zero diffs across 141 currently-translating models. That PR would have qualified for `byte-stable-refactor` in the Task 10 design.

**Estimated exception frequency:** ~1 of 100 emit-affecting PRs based on the Sprint 24/25 PR-title survey. The exception exists for the genuine refactor case; do not use it to bypass the rule for functional changes.

### Companion: `skip-emit-solve-ci` label (PR19, Sprint 26 Task 8)

Note that `byte-stable-refactor` is **distinct from** the `skip-emit-solve-ci` label (PR19 design — Sprint 26 Task 8 `DESIGN_PR19_SOLVE_TIME_CI.md`). The two labels gate different things:

| Label | Gates | Sprint of origin |
|---|---|---|
| `byte-stable-refactor` | This PR14 rule (regenerated `.gms` artifact in diff) | Sprint 26 Task 10 (this rule) |
| `skip-emit-solve-ci` | The PR19 CI workflow (pre-merge PATH solve on canaries) | Sprint 26 Task 8 |

A pure refactor PR may need both labels; a functional emit change typically gets neither.

---

## Emit-PR `.gms` Diff Workflow (PR22, Sprint 27 Prep Task 9)

**Codified per Sprint 26 retrospective recommendation PR22.**

The companion automation to the PR14 rule above. The PR14 rule says *"include a regenerated `.gms` artifact from an affected model"*; PR22 helps you and reviewers enumerate **which** artifacts are affected by an upstream `src/` change, and powers the mid-sprint retest comparison surface.

### Script

`scripts/sprint_audit/changed_emit_artifacts.py` scans `git log` for changes under `data/gamslib/mcp/` matching the emit-artifact suffixes `*_mcp.gms` and `*_mcp_presolve.gms`, grouped by triggering commit. Three output formats (`text`, `markdown`, `json`) and two report-header modes (`pr14`, `retest`).

### Per-PR usage (PR14 companion)

Before opening an emit-affecting PR, list every `.gms` artifact your branch has regenerated since branching off `main`:

```bash
# Get the PR base SHA (usually the merge-base with main):
BASE_SHA=$(git merge-base main HEAD)

.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-commit "$BASE_SHA" --format markdown --mode pr14
```

Paste the markdown output into the PR description under a `## Emit artifacts touched` heading. Reviewers use it as the checklist for PR14 §"What reviewers must do".

### Mid-sprint retest usage

At each mid-sprint retest checkpoint, generate the comparison surface relative to the Sprint Day 0 anchor commit (recorded in `docs/planning/EPIC_4/SPRINT_<N>/PLAN.md` Day 0):

```bash
SPRINT_DAY0=<the recorded Day 0 SHA>

.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-commit "$SPRINT_DAY0" --format markdown --mode retest \
    > /tmp/sprint_retest_surface.md
```

Paste `/tmp/sprint_retest_surface.md` into the retest entry in `SPRINT_LOG.md`. This replaces the Sprint 26 practice of manually maintaining the retest model list in a frozen `PLAN_PROMPTS.md` (Day 12 staleness incident).

### Why two flags (`--since-date` vs `--since-commit`)

`git log --since <DATE>` is date-only — it does not accept commit SHAs. The script exposes two distinct flags rather than one overloaded `--since`:

| Flag | When to use |
|---|---|
| `--since-date "2026-04-22"` | Quick ad-hoc lookups; OK if cross-day commit boundary doesn't matter. |
| `--since-commit <SHA>` | **Preferred for mid-sprint retests** — commit boundaries are unambiguous, eliminating timestamp-edge cases. |

### Exit codes

- `0` — success (zero or more commits found).
- `2` — invalid arguments (e.g., bad `--since-commit` SHA, both flags set, neither flag set).

### Related

- This rule's companion: `## Emit-Affecting PRs — Required .gms Artifact in Diff (PR14)` above.
- Design document: `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md`.

---

## Phase 0 Acceptance Gates (PR20, Sprint 27 Prep Task 2)

### The hard rule

**Any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` MUST have a `## Phase 0: Acceptance Gate` section in its `docs/issues/ISSUE_<N>_*.md` file BEFORE any `src/` commit lands for that issue.**

The Phase 0 section must contain exactly these 4 subsections, each rendered as a markdown `###` heading (do NOT use bold text or `####` — verification grep matches the literal `### <name>` form):

- `### Hand-Derived KKT Shape` — formal Lagrangian + stationarity / primal-feasibility / complementarity equations for the target equation(s)
- `### Expected Emit Pattern` — what the regenerated `<model>_mcp.gms` should contain (by equation name + index pattern)
- `### Verification Methodology` — explicit byte-comparison or pattern-match command(s) to run against the regenerated emit
- `### PROCEED/REPLAN Signal` — binary criteria for whether Phase 1 `src/` implementation may begin

### Why this exists

Unit tests, integration tests, and byte-stability gates are **insufficient** to catch alias-AD pipeline architectural-drift regressions. Sprint 26 had two incidents proving this:

- **PR #1379 (Phase A consolidated zero-offset builder, Sprint 26 Day 1):** shipped through PR19's CI target list with all quality gates GREEN, then PR #1399 reviewer-driven retest discovered the new gate predicate had regressed 15 non-target models with `path_syntax_error`. Filed as #1398 with the prep-task PR20 codification + PR19 target-list widening as structural mitigations.
- **PR #1394 (#1335 in-place scalar-eq fix, Sprint 26 Day 9):** shipped with `make typecheck && make format && make lint && make test` clean, but reviewer hand-derived the expected KKT shape and identified that the emit's `stat_p(tt)` body was structurally wrong (would have produced wrong solver behavior). Rolled back during PR review; reclassified as #1393 + #1335 in-place reopen.

Both incidents prove: **only hand-derived KKT comparison reliably surfaces architectural-drift regressions that GREEN quality gates miss.**

### Exception scope

Phase 0 is NOT required for changes that touch ONLY:

- `scripts/**` (pipeline / CI / audit scripts)
- `tests/**` (test-only changes; new test cases without `src/` changes)
- `docs/**` (documentation, planning docs, retrospectives)
- `.github/**` (CI workflows)
- `data/**` (regenerated artifacts; status JSON updates)

A PR that touches BOTH `src/{ad,kkt,emit}/` AND any of the exempted paths still requires Phase 0 for the `src/` portion.

### Workflow

1. **File / re-open the issue** with the bug description, reproducer, and investigation pointers.
2. **Author the `## Phase 0: Acceptance Gate` section** in `docs/issues/ISSUE_<N>_*.md` with the 4 required subsections. Use existing Phase 0 sections (e.g., `docs/issues/ISSUE_1356_*.md` from Sprint 27 Prep Task 2) as format reference.
3. **Run the Verification Methodology commands** against a prototype patch (model-name-guarded to avoid regression risk) BEFORE writing the production fix. Capture the PROCEED / REPLAN signal in the issue.
4. **If PROCEED:** proceed to Phase 1 (`src/` implementation) with the hand-derived KKT shape as the acceptance reference. Cite Phase 0 in the PR description.
5. **If REPLAN:** either revise the Phase 0 hand-derivation (if it was wrong), or rescope the issue (e.g., file a successor issue with a different fix-surface diagnosis). Do NOT commit `src/` changes against a REPLAN'd Phase 0.

### Reviewer expectations

PR reviewers for `src/{ad,kkt,emit}/`-touching PRs MUST:

- Check that the linked issue has a `## Phase 0: Acceptance Gate` section
- Verify the PR description references the Phase 0 PROCEED signal (or explicitly explains why it doesn't apply — e.g., exception-scope follow-on cleanup that doesn't change emit shape)
- Run the Verification Methodology commands locally and confirm the emit shape matches the Expected Emit Pattern

A PR missing Phase 0 should be blocked by the reviewer until Phase 0 is authored, NOT merged with a "follow-on TODO" note.

### Related

- Sprint 26 retrospective §"What We'd Do Differently" PR20 codification rationale: `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md`
- Sprint 27 Prep Task 2 (the codification of this rule): `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 2

---

## Project Structure

```
nlp2mcp/
├── src/                   # Source code
│   ├── ad/                # Automatic differentiation
│   ├── emit/              # GAMS MCP code generation
│   ├── gams/              # Parser (Lark grammar)
│   ├── ir/                # Intermediate representation
│   ├── kkt/               # KKT system assembly
│   └── utils/             # Utilities
├── tests/                 # Test suite (mirrors src/)
│   ├── unit/              # Fast, isolated tests
│   ├── integration/       # Cross-module tests
│   ├── e2e/               # End-to-end pipeline tests
│   └── validation/        # Mathematical correctness
├── examples/              # Sample GAMS NLP models
├── docs/                  # Documentation
│   ├── ad/                # AD module documentation
│   ├── architecture/      # System architecture
│   ├── emit/              # Code generation docs
│   ├── kkt/               # KKT assembly docs
│   ├── planning/          # Sprint plans & retrospectives
│   └── development/       # Development guidelines (AGENTS.md)
└── scripts/               # Development scripts
```

---

## Sprint Planning Process

This project follows a structured sprint planning process:

1. **Planning Phase**: Each sprint begins with detailed planning
   - Review PROJECT_PLAN.md for sprint scope
   - Create SPRINT_X/PLAN.md with day-by-day breakdown
   - Conduct planning reviews to identify risks
   - Create PREP_PLAN.md with pre-sprint tasks

2. **Execution Phase**: Follow the sprint plan
   - Daily progress tracking
   - Mid-sprint checkpoints (Days 3, 6, 8)
   - Integration health checks
   - Continuous testing

3. **Retrospective Phase**: Learn and improve
   - Document what went well / needs improvement
   - Create action items for next sprint
   - Update metrics and statistics

See [docs/planning/EPIC_1/README.md](docs/planning/EPIC_1/README.md) for sprint summaries and retrospectives.

---

## Getting Help

- **Documentation**: Start with [README.md](README.md) and [docs/](docs/)
- **Development Guidelines**: See [docs/development/AGENTS.md](docs/development/AGENTS.md)
- **System Architecture**: See [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)
- **Issues**: Check [GitHub Issues](https://github.com/jeffreyhorn/nlp2mcp/issues)

---

## Code of Conduct

- Be respectful and constructive
- Focus on technical merit
- Help others learn and improve
- Follow professional standards

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Current Status**: Sprint 3 Complete (602 tests passing, 89% coverage)  
**Active Development**: Sprint 4 Preparation Phase

For detailed development guidelines, workflows, and patterns, please read:
📖 **[docs/development/AGENTS.md](docs/development/AGENTS.md)**
