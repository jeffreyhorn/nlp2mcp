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

### Current (Sprint 1 - Parser & IR)

- ✅ Parse GAMS NLP subset (sets, parameters, variables, equations, bounds)
- ✅ Build intermediate representation (IR) with normalized constraints
- ✅ Support for indexed variables and equations
- ✅ Expression AST with automatic differentiation capabilities
- ✅ Comprehensive test coverage

### Planned (See [docs/planning/PROJECT_PLAN.md](docs/planning/PROJECT_PLAN.md))

- 🔄 Sprint 2: Automatic differentiation engine for gradients/Jacobians
- 📋 Sprint 3: KKT synthesis and GAMS MCP code generation
- 📋 Sprint 4: Extended language features and robustness
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

### Command Line (Planned)

```bash
# Convert NLP to MCP
nlp2mcp input.gms -o output_mcp.gms

# Specify objective sense
nlp2mcp model.gms --sense=min --output=kkt_model.gms
```

### Python API (Current)

```python
from src.ir import parser
from src.ir.normalize import normalize_model

# Parse a GAMS NLP file
model = parser.parse_model_file("examples/simple_nlp.gms")

# Normalize equations to canonical form
equations, bounds = normalize_model(model)

# Access the IR
print(f"Variables: {list(model.variables.keys())}")
print(f"Equations: {list(model.equations.keys())}")
print(f"Objective: {model.objective.sense} {model.objective.objvar}")
```

## Project Structure

```
nlp2mcp/
├── src/
│   ├── ad/           # Automatic differentiation engine (planned)
│   ├── emit/         # Code generation for GAMS MCP (planned)
│   ├── gams/         # GAMS grammar and parsing utilities
│   ├── ir/           # Intermediate representation
│   │   ├── ast.py           # Expression AST nodes
│   │   ├── model_ir.py      # Model IR data structures
│   │   ├── normalize.py     # Constraint normalization
│   │   ├── parser.py        # GAMS parser
│   │   └── symbols.py       # Symbol table definitions
│   ├── kkt/          # KKT system assembly (planned)
│   └── utils/        # Utility functions
├── tests/
│   ├── gams/         # Parser tests
│   └── ir/           # IR and normalization tests
├── examples/         # Example GAMS models
├── docs/             # Additional documentation
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

```bash
# Run all tests
make test

# Run specific test file
pytest tests/ir/test_normalize.py -v

# Run with coverage
pytest --cov=src tests/
```

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

## Supported GAMS Subset (v1)

### Declarations
- ✅ `Sets` with explicit members
- ✅ `Aliases`
- ✅ `Parameters` (scalar and indexed)
- ✅ `Scalars`
- ✅ `Variables` (scalar and indexed)
- ✅ `Equations` (scalar and indexed)

### Expressions
- ✅ Arithmetic: `+`, `-`, `*`, `/`, `^`
- ✅ Functions: `exp`, `log`, `sqrt`, `sin`, `cos`, `tan`
- ✅ Aggregation: `sum(i, expr)`
- ✅ Comparisons: `=`, `<>`, `<`, `>`, `<=`, `>=`
- ✅ Logic: `and`, `or`

### Equations
- ✅ Relations: `=e=` (equality), `=l=` (≤), `=g=` (≥)
- ✅ Variable bounds: `.lo`, `.up`, `.fx`

### Model
- ✅ `Model` declaration with equation lists or `/all/`
- ✅ `Solve` statement with `using NLP` and objective

### Not Yet Supported
- ❌ Control flow (`Loop`, `If`, `While`)
- ❌ `$` directives (`$include`, `$if`, etc.)
- ❌ `Table` data blocks
- ❌ Non-differentiable functions (`abs`, `min`, `max`)
- ❌ External/user-defined functions

## Documentation

- [docs/concepts/IDEA.md](docs/concepts/IDEA.md) - Original concept: How KKT conditions transform NLP to MCP
- [docs/concepts/NLP2MCP_HIGH_LEVEL.md](docs/concepts/NLP2MCP_HIGH_LEVEL.md) - Feasibility study and implementation blueprint
- [docs/planning/PROJECT_PLAN.md](docs/planning/PROJECT_PLAN.md) - Detailed 5-sprint development plan
- [AGENTS.md](AGENTS.md) - Agent-based development notes

## Contributing

This project is in active development (Sprint 1 complete). Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run `make format` and `make lint`
5. Run `make test` to ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Based on the mathematical framework of KKT conditions for nonlinear optimization
- Uses [Lark](https://github.com/lark-parser/lark) for parsing GAMS syntax
- Inspired by GAMS/PATH and other MCP solvers

## Roadmap

- **v0.1.0** (Sprint 1): ✅ Parser and IR - COMPLETE
- **v0.2.0** (Sprint 2): Automatic differentiation
- **v0.3.0** (Sprint 3): KKT synthesis and MCP code generation
- **v0.4.0** (Sprint 4): Extended features and robustness
- **v1.0.0** (Sprint 5): Production-ready with docs and PyPI release

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
