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
