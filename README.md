# NLP2MCP: Convert GAMS NLP to MCP via KKT Conditions

![CI](https://github.com/jeffreyhorn/nlp2mcp/workflows/CI/badge.svg)
![Lint](https://github.com/jeffreyhorn/nlp2mcp/workflows/Lint/badge.svg)

A Python tool that transforms Nonlinear Programming (NLP) models written in GAMS into equivalent Mixed Complementarity Problems (MCP) by generating the Karush-Kuhn-Tucker (KKT) conditions.

## Overview

This project automates the process of converting a GAMS NLP model into its KKT-based MCP formulation, which is useful for:

- **Mathematical research**: Analyzing stationarity conditions of nonlinear programs
- **Solver development**: Testing MCP solvers on problems derived from NLPs
- **Educational purposes**: Understanding the relationship between NLP and MCP formulations
- **Advanced modeling**: Working with equilibrium problems and complementarity conditions

## Background

The standard recipe for NLP → MCP transformation is:

1. Start with a nonlinear program (NLP)
2. Write down its KKT (Karush-Kuhn-Tucker) conditions
3. Encode those KKT conditions as a Mixed Complementarity Problem (MCP):
   - Equations for stationarity and equality constraints
   - Complementarity pairs for inequalities and bounds

For more details, see [docs/concepts/IDEA.md](docs/concepts/IDEA.md) and [docs/concepts/NLP2MCP_HIGH_LEVEL.md](docs/concepts/NLP2MCP_HIGH_LEVEL.md).

## Features

### Current (Sprint 1-3 Complete)

**Sprint 1: Parser & IR**
- ✅ Parse GAMS NLP subset (sets, parameters, variables, equations, bounds)
- ✅ Build intermediate representation (IR) with normalized constraints
- ✅ Support for indexed variables and equations
- ✅ Expression AST with symbolic differentiation capabilities
- ✅ Comprehensive test coverage

**Sprint 2: Symbolic Differentiation**
- ✅ Symbolic differentiation engine for computing derivatives
- ✅ **Expression simplification** with configurable modes:
  - **Advanced** (default): Term collection, constant/like-term/coefficient collection, cancellation
  - **Basic**: Constant folding, zero elimination, identity elimination
  - **None**: No simplification for debugging
- ✅ Index-aware differentiation (distinguishes scalar vs indexed variables)
- ✅ Objective gradient computation with sparse structure
- ✅ Constraint Jacobian computation (equality and inequality)
- ✅ Support for all standard functions (arithmetic, power, exp, log, sqrt, trig)
- ✅ Sum aggregation handling with index matching
- ✅ Finite-difference validation for derivative correctness
- ✅ High-level API: `compute_derivatives(model_ir)` → (gradient, J_eq, J_ineq)

**Sprint 3: KKT Synthesis & GAMS MCP Generation** ✅ **COMPLETE**
- ✅ KKT system assembly (stationarity, complementarity, multipliers)
- ✅ GAMS MCP code generation with proper syntax
- ✅ **Indexed stationarity equations** (Issue #47 fix - major refactoring)
- ✅ Original symbols preservation (sets, parameters, aliases)
- ✅ Variable kind preservation (Positive, Binary, Integer, etc.)
- ✅ Indexed bounds handling (per-instance complementarity pairs)
- ✅ Infinite bounds filtering (skip ±∞ bounds)
- ✅ Duplicate bounds exclusion (prevent redundant complementarity)
- ✅ Objective variable special handling
- ✅ Command-line interface (CLI)
- ✅ Golden test suite (end-to-end regression testing)
- ✅ Optional GAMS syntax validation
- ✅ Comprehensive documentation (KKT assembly, GAMS emission)
- ✅ 602 tests passing, 100% deterministic output

**Sprint 4: Extended Features & Robustness** ✅ **COMPLETE**

*Preparation Phase* (see [docs/planning/SPRINT_4/PREP_PLAN.md](docs/planning/SPRINT_4/PREP_PLAN.md)):
- ✅ Task 1: Resolve Issue #47 (indexed stationarity equations)
- ✅ Task 2: Create Known Unknowns List ([KNOWN_UNKNOWNS.md](docs/planning/SPRINT_4/KNOWN_UNKNOWNS.md))
- ✅ Task 3: Set Up PATH Solver Validation (PATH solver verified, test framework created)
- ✅ Task 4: Add Performance Benchmarking (7 benchmarks, scalability tests)
- ✅ Task 5: Improve Error Messages (error hierarchy, 6 error classes)
- ✅ Task 6: Create Edge Case Test Matrix (29 test cases, 6 categories)
- ✅ Task 7: Formalize Checkpoint Templates ([CHECKPOINT_TEMPLATES.md](docs/process/CHECKPOINT_TEMPLATES.md))
- ✅ Task 8: Review and Update Documentation (Issue #47 lessons documented)
- ✅ Task 9: Plan Sprint 4 Scope and Schedule ([PLAN.md](docs/planning/SPRINT_4/PLAN.md))

*Implementation Phase* (see [docs/planning/SPRINT_4/PLAN.md](docs/planning/SPRINT_4/PLAN.md)):
- ✅ Day 1: `$include` and Preprocessing (8h)
- ✅ Day 2: `Table` Data Blocks (8h)
- ✅ Day 3: `min/max` Reformulation - Part 1 (Infrastructure) (8h)
- ✅ Day 4: `min/max` Reformulation - Part 2 (Implementation) (8h)
- ✅ Day 5: `abs(x)` Handling and Fixed Variables (`x.fx`) (8h)
- ✅ Day 6: Scaling Implementation + Developer Ergonomics Part 1 (8h)
- ✅ Day 7: Diagnostics + Developer Ergonomics Part 2 (8h)
- ✅ Day 8: PATH Solver Validation and Testing (7.5h)
- ✅ Day 9: Integration Testing, Documentation, and Examples (8h)
- ✅ Day 10: Polish, Buffer, and Sprint Wrap-Up (8h)

### Planned (See [docs/planning/PROJECT_PLAN.md](docs/planning/PROJECT_PLAN.md))

- 📋 Sprint 5: Packaging, documentation, and ecosystem integration

## Installation

### Requirements

- Python 3.12 or higher
- pip 21.3 or higher (for pyproject.toml support)

### For Development

```bash
# Clone the repository
git clone <repository-url>
cd nlp2mcp

# Create a virtual environment with Python 3.12+
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
make install-dev
```

### For Use

```bash
pip install nlp2mcp  # (Not yet published to PyPI)
```

## Usage

### Command Line Interface

```bash
# Convert NLP to MCP
nlp2mcp input.gms -o output_mcp.gms

# Print to stdout
nlp2mcp input.gms

# Verbose output (show pipeline stages)
nlp2mcp input.gms -o output.gms -v

# Very verbose (show detailed statistics)
nlp2mcp input.gms -o output.gms -vv

# Quiet mode (errors only)
nlp2mcp input.gms -o output.gms --quiet

# Show model statistics
nlp2mcp input.gms -o output.gms --stats

# Export Jacobian structure for analysis
nlp2mcp input.gms -o output.gms --dump-jacobian jacobian.mtx

# Apply Curtis-Reid scaling for ill-conditioned systems
nlp2mcp input.gms -o output.gms --scale auto

# Enable smooth abs() approximation
nlp2mcp input.gms -o output.gms --smooth-abs

# Customize model name
nlp2mcp input.gms -o output.gms --model-name my_mcp_model

# Disable explanatory comments
nlp2mcp input.gms -o output.gms --no-comments

# Show excluded duplicate bounds
nlp2mcp input.gms -o output.gms --show-excluded
```

**CLI Options:**
- `-o, --output FILE`: Output file path (default: stdout)
- `-v, --verbose`: Increase verbosity (stackable: -v, -vv, -vvv)
- `-q, --quiet`: Suppress non-error output
- `--model-name NAME`: Custom GAMS model name (default: mcp_model)
- `--show-excluded / --no-show-excluded`: Show duplicate bounds excluded (default: no)
- `--no-comments`: Disable explanatory comments in output
- `--stats`: Print model statistics (equations, variables, nonzeros)
- `--dump-jacobian FILE`: Export Jacobian structure to Matrix Market format
- `--scale {none,auto,byvar}`: Apply scaling (default: none)
- `--simplification {none,basic,advanced}`: Expression simplification mode (default: advanced)
- `--smooth-abs`: Enable smooth abs() approximation via sqrt(x²+ε)
- `--smooth-abs-epsilon FLOAT`: Epsilon for abs smoothing (default: 1e-6)
- `--help`: Show help message

### Expression Simplification

nlp2mcp automatically simplifies derivative expressions to produce more compact and efficient MCP formulations. The simplification mode can be controlled via the `--simplification` flag or configuration file.

#### Simplification Modes

**Advanced (default)** - `--simplification advanced`
- Applies all basic simplifications plus algebraic term collection

*Additive term collection:*
- **Constant collection**: `1 + x + 1 → x + 2`
- **Like-term collection**: `x + y + x + y → 2*x + 2*y`
- **Coefficient collection**: `2*x + 3*x → 5*x`
- **Term cancellation**: `x - x → 0`, `x + y - x → y`
- **Complex bases**: `x*y + 2*x*y → 3*x*y`

*Multiplicative term collection:*
- **Variable collection**: `x * x → x^2`, `x * x * x → x^3`
- **Power multiplication**: `x^2 * x^3 → x^5`
- **Mixed multiplication**: `x^2 * x → x^3`, `x * x^2 → x^3`

*Other algebraic rules:*
- **Multiplicative cancellation**: `2*x / 2 → x`, `2*x / (1+1) → x`
- **Power division**: `x^5 / x^2 → x^3`, `x / x^2 → 1/x`
- **Nested powers**: `(x^2)^3 → x^6`

Recommended for most use cases - produces cleanest output

**Basic** - `--simplification basic`
- Applies only fundamental simplification rules:
  - Constant folding: `2 + 3 → 5`, `4 * 5 → 20`
  - Zero elimination: `x + 0 → x`, `0 * x → 0`
  - Identity elimination: `x * 1 → x`, `x / 1 → x`, `x^1 → x`
  - Algebraic identities: `x - x → 0`, `x / x → 1`
- Use when you want minimal transformation of expressions

**None** - `--simplification none`
- No simplification applied
- Derivative expressions remain in raw differentiated form
- Useful for debugging or understanding the differentiation process
- May produce very large expressions

#### Examples

```bash
# Default: advanced simplification
nlp2mcp model.gms -o output.gms

# Explicitly use advanced
nlp2mcp model.gms -o output.gms --simplification advanced

# Use basic simplification only
nlp2mcp model.gms -o output.gms --simplification basic

# Disable simplification
nlp2mcp model.gms -o output.gms --simplification none
```

#### Configuration File

You can set the default simplification mode in `pyproject.toml`:

```toml
[tool.nlp2mcp]
simplification = "advanced"  # or "basic" or "none"
scale = "none"
smooth_abs = false
```

#### When to Use Each Mode

- **Advanced** (default): Best for production use - produces cleanest, most readable output
- **Basic**: When you need predictable transformations without aggressive optimization
- **None**: For debugging, education, or when you need to see raw derivative expressions

### Complete Example

**Input** (`examples/scalar_nlp.gms`):
```gams
Variables x, obj;
Scalars a /2.0/;
Equations objective, stationarity;

objective.. obj =E= x;
stationarity.. x + a =E= 0;

Model mymodel /all/;
Solve mymodel using NLP minimizing obj;
```

**Run nlp2mcp**:
```bash
nlp2mcp examples/scalar_nlp.gms -o output_mcp.gms
```

**Output** (`output_mcp.gms`):
```gams
* Generated by nlp2mcp
* KKT System with stationarity, complementarity, and multipliers

Scalars
    a /2.0/
;

Variables
    x
    obj
    nu_objective
    nu_stationarity
;

Equations
    stat_x
    objective
    stationarity
;

stat_x.. 1 + nu_stationarity =E= 0;
objective.. obj =E= x;
stationarity.. x + a =E= 0;

Model mcp_model /
    stat_x.x,
    objective.obj,
    stationarity.nu_stationarity
/;

Solve mcp_model using MCP;
```

### Python API

```python
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.ad.gradient import compute_objective_gradient
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.kkt.assemble import assemble_kkt_system
from src.emit.emit_gams import emit_gams_mcp

# Full pipeline
model = parse_model_file("examples/simple_nlp.gms")
normalize_model(model)
gradient = compute_objective_gradient(model)
J_eq, J_ineq = compute_constraint_jacobian(model)
kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
gams_code = emit_gams_mcp(kkt, model_name="mcp_model", add_comments=True)

print(gams_code)

# Access gradient for a variable by name
grad_x_i = gradient.get_derivative_by_name("x", ("i",))  # Get ∂f/∂x(i)

# Access Jacobian entries by iterating over nonzero entries
for row_id, col_id in J_g.get_nonzero_entries():
    # Get the derivative expression
    deriv_expr = J_g.get_derivative(row_id, col_id)

    # Get equation and variable names from the index mapping
    eq_info = J_g.index_mapping.get_eq_instance(row_id)
    var_info = J_g.index_mapping.get_var_instance(col_id)

    if eq_info and var_info:
        eq_name, eq_indices = eq_info
        var_name, var_indices = var_info
        print(f"∂{eq_name}{eq_indices}/∂{var_name}{var_indices} = {deriv_expr}")

# Or access specific Jacobian entry by names
deriv = J_g.get_derivative_by_names("constraint", ("i1",), "x", ("i1",))
```

## Project Structure

```
nlp2mcp/
├── src/
│   ├── ad/           # Symbolic differentiation engine
│   │   ├── api.py              # High-level API
│   │   ├── differentiate.py    # Core differentiation rules
│   │   ├── simplify.py         # Expression simplification
│   │   ├── evaluate.py         # AST evaluation
│   │   ├── gradient.py         # Gradient computation
│   │   ├── jacobian.py         # Jacobian computation
│   │   ├── mapping.py          # Index mapping utilities
│   │   └── validation.py       # Finite-difference validation
│   ├── emit/         # Code generation for GAMS MCP (planned)
│   ├── gams/         # GAMS grammar and parsing utilities
│   ├── ir/           # Intermediate representation
│   │   ├── ast.py              # Expression AST nodes
│   │   ├── model_ir.py         # Model IR data structures
│   │   ├── normalize.py        # Constraint normalization
│   │   ├── parser.py           # GAMS parser
│   │   └── symbols.py          # Symbol table definitions
│   ├── kkt/          # KKT system assembly (planned)
│   └── utils/        # Utility functions
├── tests/
│   ├── ad/           # Differentiation tests
│   ├── gams/         # Parser tests
│   └── ir/           # IR and normalization tests
├── examples/         # Example GAMS models
├── docs/             # Additional documentation
│   ├── ad/                   # Automatic differentiation docs
│   ├── architecture/         # System architecture
│   ├── emit/                 # GAMS emission docs
│   ├── kkt/                  # KKT assembly docs
│   └── planning/             # Sprint plans and retrospectives
├── pyproject.toml    # Project configuration
├── Makefile          # Development commands
└── README.md         # This file
```

## Development

### Available Make Commands

```bash
make help         # Show all available commands
make install      # Install the package
make install-dev  # Install with dev dependencies
make lint         # Run linters (ruff, mypy)
make format       # Format code (black, ruff)
make test         # Run tests
make clean        # Remove build artifacts
```

### Running Tests

The test suite is organized into four layers for fast feedback.

📊 **[View Test Pyramid Visualization](docs/testing/TEST_PYRAMID.md)** - See test coverage breakdown by module and type.

```bash
# Run fast unit tests only (~10 seconds)
./scripts/test_fast.sh
# Or: pytest tests/unit/ -v

# Run unit + integration tests (~30 seconds)
./scripts/test_integration.sh
# Or: pytest tests/unit/ tests/integration/ -v

# Run complete test suite (~60 seconds)
./scripts/test_all.sh
# Or: pytest tests/ -v

# Run specific test category
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m e2e          # Only end-to-end tests
pytest -m validation   # Only validation tests

# Run specific test file
pytest tests/unit/ad/test_arithmetic.py -v

# Run with coverage
pytest --cov=src tests/
```

### Test Organization

```
tests/
├── unit/              # Fast tests, no file I/O (~10 tests/sec)
│   ├── ad/           # AD engine unit tests
│   ├── gams/         # Parser unit tests
│   └── ir/           # IR unit tests
├── integration/       # Cross-module tests (~5 tests/sec)
│   └── ad/           # Gradient and Jacobian integration
├── e2e/              # Full pipeline tests (~2 tests/sec)
│   └── test_integration.py
└── validation/        # Mathematical correctness (~1 test/sec)
    └── test_finite_difference.py
```

**Test Pyramid Strategy:**
- **Unit tests** (157 tests): Test individual functions/modules in isolation
- **Integration tests** (45 tests): Test cross-module interactions
- **E2E tests** (15 tests): Test full GAMS → derivatives pipeline
- **Validation tests** (169 tests): Finite-difference validation of derivatives

### Code Style

This project uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting and import sorting
- **MyPy** for type checking

Format your code before committing:

```bash
make format
make lint
```

## Examples

The `examples/` directory contains sample GAMS NLP models:

- `simple_nlp.gms` - Basic indexed NLP with objective and constraints
- `scalar_nlp.gms` - Simple scalar optimization problem
- `indexed_balance.gms` - Model with indexed balance equations
- `bounds_nlp.gms` - Demonstrates variable bounds handling
- `nonlinear_mix.gms` - Mixed nonlinear functions

## Supported GAMS Subset

### Declarations
- ✅ `Sets` with explicit members
- ✅ `Aliases`
- ✅ `Parameters` (scalar and indexed)
- ✅ `Scalars`
- ✅ `Variables` (scalar and indexed)
- ✅ `Equations` (scalar and indexed)
- ✅ `Table` data blocks *(Sprint 4)*

### Preprocessing
- ✅ `$include` directive (nested, relative paths) *(Sprint 4)*

### Comments
- ✅ GAMS inline comments (`* comment`)
- ✅ C-style line comments (`// comment`)
- ✅ Block comments (`$ontext ... $offtext`)

**Note:** Input file comments are stripped during parsing and do not appear in the output. However, the emitter can add explanatory comments to the output (controlled by `--no-comments` flag).

### Expressions
- ✅ Arithmetic: `+`, `-`, `*`, `/`, `^`
- ✅ Functions: `exp`, `log`, `sqrt`, `sin`, `cos`, `tan`
- ✅ Aggregation: `sum(i, expr)`
- ✅ Comparisons: `=`, `<>`, `<`, `>`, `<=`, `>=`
- ✅ Logic: `and`, `or`
- ✅ `min()` and `max()` (reformulated to complementarity) *(Sprint 4)*
- ✅ `abs()` (smooth approximation with `--smooth-abs`) *(Sprint 4)*

### Equations
- ✅ Relations: `=e=` (equality), `=l=` (≤), `=g=` (≥)
- ✅ Variable bounds: `.lo`, `.up`, `.fx`

### Model
- ✅ `Model` declaration with equation lists or `/all/`
- ✅ `Solve` statement with `using NLP` and objective

### Advanced Features *(Sprint 4)*
- ✅ **Scaling**: Curtis-Reid and byvar scaling (`--scale auto|byvar`)
- ✅ **Diagnostics**: Model statistics (`--stats`), Jacobian export (`--dump-jacobian`)
- ✅ **Configuration**: `pyproject.toml` support for default options
- ✅ **Logging**: Structured logging with verbosity control (`--verbose`, `--quiet`)

### Not Yet Supported
- ❌ Control flow (`Loop`, `If`, `While`)
- ❌ Other `$` directives (`$if`, `$set`, etc.)
- ❌ External/user-defined functions
- ❌ Other non-differentiable functions (floor, ceil, sign, etc.)

## Documentation

### Concepts & Planning
- [docs/concepts/IDEA.md](docs/concepts/IDEA.md) - Original concept: How KKT conditions transform NLP to MCP
- [docs/concepts/NLP2MCP_HIGH_LEVEL.md](docs/concepts/NLP2MCP_HIGH_LEVEL.md) - Feasibility study and implementation blueprint
- [docs/planning/PROJECT_PLAN.md](docs/planning/PROJECT_PLAN.md) - Detailed 5-sprint development plan
- [docs/planning/README.md](docs/planning/README.md) - Sprint summaries and retrospectives
- [docs/development/AGENTS.md](docs/development/AGENTS.md) - Agent-based development notes

### Technical Documentation

**System Architecture:**
- [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md) - Overall system data flow
- [docs/architecture/DATA_STRUCTURES.md](docs/architecture/DATA_STRUCTURES.md) - IR and KKT data structures

**Automatic Differentiation:**
- [docs/ad/README.md](docs/ad/README.md) - AD module overview and quick start
- [docs/ad/ARCHITECTURE.md](docs/ad/ARCHITECTURE.md) - Design decisions and rationale
- [docs/ad/DESIGN.md](docs/ad/DESIGN.md) - Detailed implementation approach
- [docs/ad/DERIVATIVE_RULES.md](docs/ad/DERIVATIVE_RULES.md) - Complete derivative rules reference

**KKT Assembly & Code Generation:**
- [docs/kkt/KKT_ASSEMBLY.md](docs/kkt/KKT_ASSEMBLY.md) - KKT system assembly (mathematical background, implementation)
- [docs/emit/GAMS_EMISSION.md](docs/emit/GAMS_EMISSION.md) - GAMS MCP code generation (syntax, patterns, examples)

## Contributing

**Please read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing!**

This project is in active development (Sprint 3 complete, Sprint 4 in preparation). Contributions are welcome!

### Quick Start for Contributors

1. **Read guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/development/AGENTS.md](docs/development/AGENTS.md)
2. **Setup environment**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   make install-dev
   ```
3. **Create feature branch**: `git checkout -b feature/amazing-feature`
4. **Make changes**: Follow code style in CONTRIBUTING.md
5. **Quality checks**:
   ```bash
   make format   # Auto-format code
   make lint     # Type checking and linting
   make test     # All tests must pass (602+ tests)
   ```
6. **Submit PR**: Push branch and create Pull Request on GitHub

### Requirements
- Python 3.12+ with modern type hints
- All tests passing
- Code formatted with Black + Ruff
- Type checked with mypy

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Based on the mathematical framework of KKT conditions for nonlinear optimization
- Uses [Lark](https://github.com/lark-parser/lark) for parsing GAMS syntax
- Inspired by GAMS/PATH and other MCP solvers

## Roadmap

- **v0.1.0** (Sprint 1): ✅ Parser and IR - COMPLETE
- **v0.2.0** (Sprint 2): ✅ Symbolic differentiation - COMPLETE
- **v0.3.0** (Sprint 3): ✅ KKT synthesis and MCP code generation - COMPLETE
- **v0.3.1** (Post Sprint 3): ✅ Issue #47 fix (indexed equations) - COMPLETE
- **v0.4.0** (Sprint 4): 🔄 Extended features and robustness - IN PROGRESS
- **v1.0.0** (Sprint 5): Production-ready with docs and PyPI release

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
