# Repository Guidelines for nlp2mcp

## Project Overview
**nlp2mcp** is a Python 3.12+ tool that converts GAMS NLP (Nonlinear Programming) models into equivalent MCP (Mixed Complementarity Problem) formulations by generating KKT (Karush-Kuhn-Tucker) conditions.

**Current Status**: Sprint 1 Complete - Parser and IR implementation finished with comprehensive test coverage.

## Project Structure & Module Organization

```
nlp2mcp/
├── src/                     # Source code (Python 3.12+)
│   ├── ad/                  # Automatic differentiation (Sprint 2)
│   ├── emit/                # GAMS MCP code generation (Sprint 3)
│   ├── gams/                # Grammar and parsing utilities
│   │   └── gams_grammar.lark  # GAMS NLP subset grammar
│   ├── ir/                  # Intermediate representation (Sprint 1 ✅)
│   │   ├── ast.py           # Expression AST nodes
│   │   ├── model_ir.py      # Model IR data structures
│   │   ├── normalize.py     # Constraint normalization
│   │   ├── parser.py        # GAMS parser implementation
│   │   └── symbols.py       # Symbol table definitions
│   ├── kkt/                 # KKT system assembly (Sprint 3)
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── gams/                # Parser tests (19 tests)
│   └── ir/                  # IR and normalization tests (10 tests)
├── examples/                # Sample GAMS NLP models
│   ├── simple_nlp.gms
│   ├── scalar_nlp.gms
│   ├── indexed_balance.gms
│   ├── bounds_nlp.gms
│   └── nonlinear_mix.gms
├── docs/                    # Project documentation
├── pyproject.toml           # Modern Python packaging
├── setup.py                 # Backward compatibility
├── Makefile                 # Development commands
├── README.md                # Main documentation
├── PROJECT_PLAN.md          # 5-sprint development plan
├── NLP2MCP_HIGH_LEVEL.md    # Implementation blueprint
├── IDEA.md                  # Original concept
└── NEXT_STEPS.md            # Current development status
```

## Python Version & Dependencies

- **Python**: 3.12+ (uses modern type hints: `dict`, `list`, `X | Y`, `X | None`)
- **Core Dependencies**: `lark>=1.1.9`
- **Dev Dependencies**: `pytest>=7.4.4`, `black>=23.0.0`, `ruff>=0.1.0`, `mypy>=1.0.0`

## Development Setup

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
make install-dev

# Verify installation
python --version  # Should show Python 3.12.x
```

## Build, Test, and Development Commands

All development commands are available via the Makefile, which automatically detects and uses `.venv/`:

```bash
make help         # Show all available commands
make install      # Install package
make install-dev  # Install with dev dependencies
make test         # Run pytest (29 tests)
make typecheck    # Run mypy type checker
make lint         # Run all linters (ruff + mypy + black)
make format       # Auto-format code (black + ruff)
make clean        # Remove build artifacts
```

### Manual Commands (if needed)

```bash
# Run tests with coverage
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/ir/test_normalize.py -v

# Type check only parser module
mypy src/ir/parser.py

# Format specific directory
black src/ir/
```

## Coding Style & Naming Conventions

### Python 3.12 Modern Style
- **Type hints**: Use `dict`, `list`, `tuple` instead of `Dict`, `List`, `Tuple`
- **Union types**: Use `X | Y` instead of `Union[X, Y]`
- **Optional types**: Use `X | None` instead of `Optional[X]`
- **Imports**: Use `collections.abc.Iterable` instead of `typing.Iterable`
- **zip() calls**: Always use explicit `strict=True` or `strict=False` parameter

### Code Formatting
- **Black**: Line length 100, target Python 3.12
- **Ruff**: Enforces pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- **Run before commit**: `make format && make lint`

### Naming Conventions
- **Modules/functions**: `snake_case` (e.g., `normalize_equation`, `parse_model`)
- **Classes**: `CapWords` (e.g., `ModelIR`, `NormalizedEquation`, `VarRef`)
- **Constants**: `UPPER_CASE` (e.g., `INF`, `WRAPPER_NODES`)
- **GAMS keywords**: Mirror GAMS conventions when representing them

### Type Hints
- Use dataclasses for IR structures (already using `@dataclass(frozen=True)`)
- Add type hints to function signatures
- Use `from __future__ import annotations` for forward references
- MyPy configuration is pragmatic (not strict) to allow Lark tree manipulation

## Testing Guidelines

### Test Organization
- **Mirror structure**: `tests/ir/` for `src/ir/`, `tests/gams/` for parsing
- **Naming**: `test_<behavior>.py` files, `test_<specific_case>` functions
- **Current coverage**: 29 tests (10 IR, 19 parser tests)

### Test Best Practices
```python
# Use pytest parametrization for variants
@pytest.mark.parametrize("relation,expected", [
    (Rel.EQ, Rel.EQ),
    (Rel.GE, Rel.LE),  # Gets flipped
    (Rel.LE, Rel.LE),
])
def test_normalize_relation(relation, expected):
    ...

# Load examples from files
def test_example_files_parse():
    repo_root = Path(__file__).resolve().parents[2]
    model = parser.parse_model_file(repo_root / "examples" / "simple_nlp.gms")
    assert model.equations
```

### Running Tests
- **All tests**: `make test` or `pytest tests/ -v`
- **Specific module**: `pytest tests/ir/ -v`
- **With coverage**: `pytest --cov=src tests/`
- **Keep green**: All tests must pass before committing

## Commit & Pull Request Guidelines

### Commit Messages
Format: `<scope>: <imperative subject>` (max 72 chars)

```
✅ Good:
ir: add support for indexed parameter bounds
parser: fix variable domain resolution for aliases
tests: add coverage for scalar equation normalization

❌ Bad:
fixed stuff
updated code
wip
```

### Commit Body
- Explain **why** the change was needed
- Reference planning docs if design changed
- Link to related issues/PRs
- Include test results summary

Example:
```
ir: normalize inequality relations to canonical form

All inequalities are now converted to <= 0 form during normalization,
making KKT generation simpler. This aligns with the approach described
in PROJECT_PLAN.md Sprint 1.

Tests: All 29 tests passing
Refs: #12
```

### Pull Request Guidelines
1. **Title**: Clear, imperative description
2. **Description**: Include:
   - Problem being solved
   - Solution approach
   - Any technical debt or follow-up work
   - Test results (`make test` output)
3. **Before submitting**:
   ```bash
   make typecheck # Check type safety
   make format    # Auto-format
   make lint      # Check style
   make test      # Run tests
   ```
4. **Review requirements**:
   - All tests passing
   - No lint errors
   - Documentation updated if needed
   - Grammar changes require second reviewer

## Grammar & Parser Changes

- **Grammar file**: `src/gams/gams_grammar.lark`
- **Update comments**: When changing tokens or precedence
- **Sync docs**: Update supported subset in `README.md`
- **Add tests**: Include regression test in `tests/gams/test_parser.py`
- **Examples**: Add `.gms` file to `examples/` if introducing new syntax

## Documentation Updates

When making changes, update relevant docs:
- **README.md**: User-facing features, installation, usage
- **PROJECT_PLAN.md**: Sprint progress, deliverables status
- **NEXT_STEPS.md**: Current task list and priorities
- **Code comments**: Complex algorithms, non-obvious decisions

## Roadmap & Sprints

- **✅ Sprint 1** (Complete): Parser and IR
- **🔄 Sprint 2** (Next): Automatic differentiation engine
- **📋 Sprint 3**: KKT synthesis and GAMS MCP codegen
- **📋 Sprint 4**: Extended features and robustness
- **📋 Sprint 5**: Packaging, docs, PyPI release

See `PROJECT_PLAN.md` for detailed sprint breakdown.

## Common Development Tasks

### Adding a new expression type to AST
1. Add dataclass to `src/ir/ast.py`
2. Update parser in `src/ir/parser.py` to handle it
3. Add test cases in `tests/ir/`
4. Update normalization if needed in `src/ir/normalize.py`

### Adding a new GAMS syntax feature
1. Update grammar in `src/gams/gams_grammar.lark`
2. Add parser handler in `src/ir/parser.py`
3. Add example `.gms` file in `examples/`
4. Add test in `tests/gams/test_parser.py`
5. Update supported features in `README.md`

### Debugging parser issues
1. Check grammar syntax: `python -c "from src.ir.parser import _build_lark; _build_lark()"`
2. Print parse tree: Use `parse_file()` and inspect tree
3. Use `pytest -xvs` for verbose test output with immediate stop on failure

## Questions & Support

- **Issues**: Open GitHub issues for bugs/features
- **Discussions**: Use GitHub discussions for questions
- **Contributing**: See commit/PR guidelines above

## Notes for AI Agents

- Always run `make format` before suggesting code changes
- Verify imports work with `from src.ir import parser`
- Test changes with `make test` before marking complete
- Modern Python 3.12 syntax is enforced by ruff
- MyPy errors in parser are expected due to dynamic Lark manipulation
