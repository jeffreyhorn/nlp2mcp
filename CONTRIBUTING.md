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
