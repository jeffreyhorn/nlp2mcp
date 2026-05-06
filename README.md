# NLP2MCP: Convert GAMS NLP to MCP via KKT Conditions

![CI](https://github.com/jeffreyhorn/nlp2mcp/workflows/CI/badge.svg)
![Lint](https://github.com/jeffreyhorn/nlp2mcp/workflows/Lint/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/nlp2mcp.svg)](https://pypi.org/project/nlp2mcp/)
[![Python Support](https://img.shields.io/pypi/pyversions/nlp2mcp.svg)](https://pypi.org/project/nlp2mcp/)

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

Epic 1 (Sprints 1-5) is complete, delivering core NLP to MCP transformation capabilities. For detailed sprint summaries, see [docs/planning/EPIC_1/SUMMARY.md](docs/planning/EPIC_1/SUMMARY.md).

Epic 2 (Sprints 6-12) is complete, expanding parser coverage to 100% (28/28 models), adding aggressive simplification with 26.19% term reduction, and establishing comprehensive CI infrastructure. For detailed sprint summaries, see [docs/planning/EPIC_2/SUMMARY.md](docs/planning/EPIC_2/SUMMARY.md).

Epic 3 (Sprints 13-17) is complete, delivering GAMSLIB testing infrastructure, automated reporting, and the v1.1.0 release. For detailed sprint summaries, see [docs/planning/EPIC_3/SUMMARY.md](docs/planning/EPIC_3/SUMMARY.md).

Epic 4 (Sprints 18-28) targets the GAMSLIB convex-continuous corpus with the goal of bringing the full pipeline (parse → translate → solve → match NLP reference) up across as many models as possible. Sprints 18-25 are complete; Sprint 26 is the next planned cycle.

**Sprint 25 final metrics (2026-05-05, in-scope = 142 convex-continuous models):**

| Stage | Count | % of in-scope | Δ vs Sprint 18 baseline |
|---|---:|---:|---:|
| Parse | 142/142 | 100.0% | +81 (61→142, after gamslib scope expansion + grammar coverage work) |
| Translate | 133/142 | 93.7% | +85 (48→133) |
| Solve | 104/133 | 78.2% | +84 (20→104) |
| Full Pipeline (match NLP reference) | 60/142 | 42.3% | +53 (7→60) |
| Tests | 4,735 passing | — | +1,441 (3,294→4,735) |

**Sprint 25 highlights:** Day 5 pivot disproved the original Pattern A alias-AD hypothesis on three Phase 1 models (qabel, abel, launch) via a reusable trace + emitted-artifact + formal-derivative methodology; Pattern C narrowed to launch-shape alias-of-IndexOffset (#1306); fix-in-place series #1338..#1352 recovered the original Checkpoint 2 NO-GO (Match 52→60, Solve 92→104, model_infeasible 14→4); WS4 small priorities #1270 (multi-solve gate Approach A — saras driver) and #1271 (`_loop_tree_to_gams` dispatcher refactor, ~140 LOC removed, byte-diff verified across all 141 currently-translating models). For full sprint history and per-sprint metrics, see [docs/planning/EPIC_4/PROJECT_PLAN.md](docs/planning/EPIC_4/PROJECT_PLAN.md) §"Rolling KPIs & Tracking" and individual sprint retrospectives under `docs/planning/EPIC_4/SPRINT_*/SPRINT_RETROSPECTIVE.md`.

## Installation

### Requirements

- Python 3.11 or higher
- pip 21.3 or higher

### Quick Start

Install from PyPI:

```bash
pip install nlp2mcp
```

Verify installation:

```bash
nlp2mcp --help
```

### From Source (Development)

For contributing or development:

```bash
# Clone the repository
git clone https://github.com/jeffreyhorn/nlp2mcp.git
cd nlp2mcp

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
make install-dev

# Or manually:
pip install -e .
pip install -r requirements.txt
```

### Beta/Pre-release Versions

To test beta releases:

```bash
# Install specific version
pip install nlp2mcp==0.5.0b0

# Or install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    nlp2mcp

# Or install directly from GitHub
pip install git+https://github.com/jeffreyhorn/nlp2mcp.git
```

## Usage

### Command Line Interface

Note: the package exposes a console script `nlp2mcp` (defined in `pyproject.toml` as
`[project.scripts] nlp2mcp = "src.cli:main"`). After installing the package (for example
with `pip install -e .` or `pip install nlp2mcp`), the `nlp2mcp` command will be available on your PATH
and will invoke `src.cli:main`.

If you prefer not to install the package, you can run the CLI directly from the repository with:

```bash
python -m src.cli examples/simple_nlp.gms -o output_mcp.gms
```


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

# NLP pre-solve for non-convex models (warm-start MCP duals)
nlp2mcp input.gms -o output.gms --nlp-presolve
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
- `--simplification {none,basic,advanced,aggressive}`: Expression simplification mode (default: advanced)
- `--smooth-abs`: Enable smooth abs() approximation via sqrt(x²+ε)
- `--smooth-abs-epsilon FLOAT`: Epsilon for abs smoothing (default: 1e-6)
- `--nlp-presolve`: Solve the original NLP first to warm-start MCP dual variables (helps non-convex models converge)
- `--check-convexity-numerical`: Run computational convexity test (requires `-o`, GAMS, and a source checkout; compares cold-start vs warm-start objectives to detect non-convexity)
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

**Aggressive** - `--simplification aggressive` *(Sprint 11)*
- Applies all advanced simplifications plus 10 additional algebraic transformations and Common Subexpression Elimination (CSE)
- **High priority transformations (T1-T3):**
  - Common factor extraction: `a*x + a*y → a*(x + y)`
  - Fraction combining: `a/c + b/c → (a + b)/c`
  - Division simplification: `(x*y)/y → x`
  - Associativity normalization: `(a + b) + c → a + b + c`
- **Medium priority transformations (T4):**
  - Power rules: `x^a * x^b → x^(a+b)`, `(x^a)^b → x^(a*b)`
  - Logarithm rules: `log(a*b) → log(a) + log(b)`, `log(a^n) → n*log(a)`
  - Trigonometric identities: `sin(x)^2 + cos(x)^2 → 1`
  - Nested operation simplification: `x*y*z*x → x^2*y*z`
- **Low priority transformations (T5 - CSE):**
  - Nested CSE: Extracts repeated complex subexpressions (≥3 occurrences)
  - Multiplicative CSE: Extracts repeated multiplication patterns (≥4 occurrences)
  - Aliasing-aware CSE: Reuses existing variable aliases instead of creating new temps
- Use for large models with complex derivatives requiring maximum simplification
- May create temporary variables for CSE and has slightly longer conversion time

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

# Use aggressive simplification (Sprint 11: 10 transforms + CSE)
nlp2mcp model.gms -o output.gms --simplification aggressive

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

The installed package exposes its modules under the `src.*` namespace (per `pyproject.toml` `[tool.setuptools.packages.find] include = ["src*"]`). After an editable install (`pip install -e .`) you can import them directly:

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
```

Equivalent CLI invocation:

```bash
nlp2mcp examples/simple_nlp.gms -o output_mcp.gms     # installed
python -m src.cli examples/simple_nlp.gms -o output_mcp.gms  # from source checkout
```

## Project Structure

```
nlp2mcp/
├── src/
│   ├── ad/           # Symbolic differentiation engine
│   │   ├── api.py                  # High-level differentiation API
│   │   ├── ad_core.py              # Core symbolic operations
│   │   ├── derivative_rules.py     # Per-function derivative rules
│   │   ├── evaluator.py            # AST evaluation
│   │   ├── gradient.py             # Objective gradient
│   │   ├── jacobian.py             # Equality Jacobian
│   │   ├── constraint_jacobian.py  # Constraint Jacobian (eq + ineq)
│   │   ├── index_mapping.py        # Index/instance enumeration
│   │   ├── lp_coefficients.py      # LP coefficient extraction
│   │   ├── minmax_flattener.py     # min/max smoothing
│   │   ├── sparsity.py             # Sparsity tracking
│   │   ├── term_collection.py      # Like-term + power collection
│   │   └── validation.py           # Finite-difference validation
│   ├── emit/         # GAMS MCP code generation
│   │   ├── emit_gams.py            # Top-level emitter
│   │   ├── equations.py            # Equation block emit
│   │   ├── expr_to_gams.py         # Expression → GAMS string
│   │   ├── model.py                # Model statement emit
│   │   ├── original_symbols.py     # Source-symbol re-emission
│   │   └── templates.py            # Comment / banner templates
│   ├── gams/         # GAMS grammar (Lark)
│   ├── ir/           # Intermediate representation
│   │   ├── ast.py                  # Expression AST nodes
│   │   ├── condition_eval.py       # Static $cond evaluation
│   │   ├── diagnostics.py          # Parse-time diagnostics
│   │   ├── metrics.py              # Model statistics
│   │   ├── minmax_detection.py     # min/max detection
│   │   ├── model_ir.py             # Model IR data structures
│   │   ├── normalize.py            # Constraint normalization
│   │   ├── parser.py               # GAMS parser (parse tree → IR)
│   │   ├── preprocessor.py         # $include / $ifThen / macros
│   │   ├── scalar_offset_resolver.py  # IndexOffset resolution
│   │   ├── simplification_pipeline.py # Simplification orchestration
│   │   ├── symbols.py              # Symbol table definitions
│   │   └── transformations/        # IR rewriting passes
│   ├── kkt/          # KKT system assembly
│   │   ├── assemble.py             # Top-level KKT assembly
│   │   ├── complementarity.py      # Comp pairs (bounds + ineq)
│   │   ├── empty_equation_detector.py
│   │   ├── kkt_system.py           # KKT data structures
│   │   ├── naming.py               # Multiplier / equation naming
│   │   ├── objective.py            # Objective expansion
│   │   ├── partition.py            # Equality / inequality split
│   │   ├── reformulation.py        # MCP reformulations
│   │   ├── scaling.py              # Curtis-Reid / byvar scaling
│   │   ├── sqr_reformulation.py    # power(x,2) → x*x
│   │   └── stationarity.py         # Stationarity equations
│   ├── validation/   # Multi-solve driver gate (#1265, #1270)
│   └── utils/        # Utility functions
├── tests/
│   ├── unit/         # Fast unit tests (~10s)
│   ├── integration/  # Integration tests (~60s)
│   ├── e2e/          # End-to-end tests
│   └── validation/   # Validation tests
├── examples/         # Example GAMS models
├── data/gamslib/     # GAMSLIB pipeline (raw sources, MCP outputs, status)
├── docs/             # Documentation
│   ├── ad/                   # AD module docs
│   ├── architecture/         # System architecture
│   ├── concepts/             # Original concepts (IDEA, NLP2MCP_HIGH_LEVEL)
│   ├── emit/                 # GAMS emission docs
│   ├── issues/               # In-tree issue tracking
│   ├── kkt/                  # KKT assembly docs
│   └── planning/             # Per-Epic plans, sprints, retrospectives
├── scripts/gamslib/  # Pipeline runners + status reporting
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

# Run tests in parallel (faster, ~2 minutes for full suite)
pytest -n 4             # Use 4 workers
pytest -n auto          # Auto-detect CPU count
```

**Parallel Testing:** The test suite supports parallel execution using `pytest-xdist`. Running with `-n 4` reduces test time from ~3-4 minutes to ~2 minutes. All tests are isolated and safe for parallel execution.

## Test Organization

The test suite is split into unit, integration, e2e, and validation layers. You can run the different subsets with the scripts in `./scripts/` or via pytest directly. End of Sprint 25 (2026-05-05): **4,735 tests passing** in `make test` (10 skipped, 2 xfailed). For per-layer marker counts you can reproduce locally:

```bash
# Total collected tests
python3 -m pytest --collect-only -q | wc -l

# Per-marker counts
python3 -m pytest -m unit --collect-only -q | wc -l
python3 -m pytest -m integration --collect-only -q | wc -l
python3 -m pytest -m e2e --collect-only -q | wc -l
python3 -m pytest -m validation --collect-only -q | wc -l
```

Typical layout:

```
tests/
├── unit/
├── integration/
├── e2e/
└── validation/
```

Test pyramid guidance: prefer fast unit tests during development, run integration/e2e for cross-module confidence, and run the full validation/validation suite before releases.

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
- ✅ `Table` data blocks

### Comments
- ✅ GAMS inline comments (`* comment`)
- ✅ C-style line comments (`// comment`)
- ✅ Block comments (`$ontext ... $offtext`)

**Note:** Input file comments are stripped during parsing and do not appear in the output. However, the emitter can add explanatory comments to the output (controlled by `--no-comments` flag). For full preprocessor / `$`-directive coverage see §"Preprocessor / Compilation Directives" below.

### Expressions
- ✅ Arithmetic: `+`, `-`, `*`, `/`, `^`, `**`
- ✅ Index offsets: `i+1`, `t-2`, etc. (constant integer offsets)
- ✅ Differentiable functions: `exp`, `log`, `log2`, `log10`, `sqrt`, `sin`, `cos`, `tan`, `power(x,n)`, `sqr(x)`, `abs()` (smooth approximation with `--smooth-abs`)
- ✅ Set/index intrinsics: `ord(i)`, `card(i)`, `sameas(i, j)`, `i.first`, `i.last`, `i.pos`
- ✅ Aggregation: `sum(i, expr)`, `prod(i, expr)`, `smax(i, expr)`, `smin(i, expr)`
- ✅ Conditional aggregation: `sum(i$cond, expr)` and `(i,j)$cond` tuple domains
- ✅ Comparisons: `=`, `<>`, `<`, `>`, `<=`, `>=`
- ✅ Logic: `and`, `or`, `not`
- ✅ `min()` / `max()` (reformulated to complementarity)
- ✅ Dollar conditionals: `expr$cond`, `lvalue$cond = rhs`

### Equations
- ✅ Relations: `=e=` (equality), `=l=` (≤), `=g=` (≥)
- ✅ Variable bounds: `.lo`, `.up`, `.fx` (scalar + indexed + expression-valued)
- ✅ Variable scaling: `.scale` (Sprint 23 #835)

### Control Flow
- ✅ `Loop(set, ...)` and filtered `Loop(i$cond, ...)` (parser + emitter — Sprint 25 #1271 dispatcher refactor unified the substituting and non-substituting paths)
- ✅ `If(cond, then ; elseif cond, ... ; else ...)`
- ✅ `While(cond, body)`

### Preprocessor / Compilation Directives
- ✅ `$include` (nested, relative paths)
- ✅ `$if`, `$ifThen / $endIf / $else / $elseIf` (#705 + Sprint 24 #1264 partssupply)
- ✅ `$set` / `$setglobal`, macro expansion in source
- ✅ `$ontext / $offtext`, `$onEcho / $offEcho`, `$onEps / $offEps`
- ✅ `$title`, `$eolcom`, `$onImplicitAssign / $offImplicitAssign`
- ✅ `$onMultiR` / `$offMultiR`

### Model
- ✅ `Model` declaration with equation lists or `/all/`
- ✅ `Solve` statement with `using NLP|DNLP|QCP|MCP|CNS [minimizing|maximizing] <objvar>`

### Advanced Features
- ✅ **NLP pre-solve**: `--nlp-presolve` warm-starts MCP from NLP optimum (helps non-convex models)
- ✅ **Scaling**: Curtis-Reid and byvar scaling (`--scale auto|byvar`)
- ✅ **Diagnostics**: Model statistics (`--stats`), Jacobian export (`--dump-jacobian`)
- ✅ **Configuration**: `pyproject.toml` support for default options
- ✅ **Logging**: Structured logging with verbosity control (`--verbose`, `--quiet`)
- ✅ **Multi-solve driver gate** (Sprints 24-25, #1265 + #1270): refuses Dantzig–Wolfe / column-generation / saras-style primal-dual scripts where the converged objective is an iterative fixed point rather than a single NLP's optimum

### Not Yet Supported
- ❌ True non-differentiable functions at the AD layer: `floor`, `ceil`, `sign`, `mod`, `round`. These parse, but their derivatives are not implemented (the only smoothable case today is `abs()` via `--smooth-abs`).
- ❌ Stochastic / sampling functions: `uniform`, `normal`, `gamma`, `loggamma`, `psi`. Parse but cannot be differentiated.
- ❌ External / user-defined functions
- ❌ Parameter-valued `IndexOffset` (e.g. `x(i+li(k))` where `li` is a `Parameter`). Tracked in [#1224](https://github.com/jeffreyhorn/nlp2mcp/issues/1224) for Sprint 26.
- ❌ MIP / MINLP / discrete variables. Out of KKT scope by design.

## Documentation

### Concepts & Planning
- [docs/concepts/IDEA.md](docs/concepts/IDEA.md) - Original concept: How KKT conditions transform NLP to MCP
- [docs/concepts/NLP2MCP_HIGH_LEVEL.md](docs/concepts/NLP2MCP_HIGH_LEVEL.md) - Feasibility study and implementation blueprint

**Per-Epic plans** (each Epic groups several sprints around a theme):

| Epic | Sprints | Focus | PROJECT_PLAN | README |
|---|---|---|---|---|
| 1 | 1-5 | Parser, AD, KKT synthesis, packaging | [PROJECT_PLAN](docs/planning/EPIC_1/PROJECT_PLAN.md) | [README](docs/planning/EPIC_1/README.md) |
| 2 | 6-12 | Parser coverage to 100% (28/28 fixtures), aggressive simplification, CI | [PROJECT_PLAN](docs/planning/EPIC_2/PROJECT_PLAN.md) | — |
| 3 | 13-17 | GAMSLIB testing infrastructure, automated reporting, v1.1.0 release | [PROJECT_PLAN](docs/planning/EPIC_3/PROJECT_PLAN.md) | — |
| 4 | 18-28 | GAMSLIB convex-continuous corpus: parse → translate → solve → match | [PROJECT_PLAN](docs/planning/EPIC_4/PROJECT_PLAN.md) | — |

For per-sprint detail under any Epic, see `docs/planning/EPIC_N/SPRINT_M/SPRINT_RETROSPECTIVE.md` (where applicable). Sprint 25 retrospective lives at [docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md](docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md).

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

This project is in active development. Sprint 25 (Epic 4 — GAMSLIB corpus pipeline) closed 2026-05-05; Sprint 26 starts next with focus on Pattern C gate generalization, Pattern A cohort reclassification, and AD residuals on `otpop`. Contributions are welcome!

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
   make test     # All tests must pass (4,735+ as of Sprint 25)
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

**Epic 1 — Foundations (Sprints 1-5):**
- **v0.1.0** (Sprint 1): ✅ Parser and IR
- **v0.2.0** (Sprint 2): ✅ Symbolic differentiation
- **v0.3.0** (Sprint 3): ✅ KKT synthesis and MCP code generation
- **v0.3.1** (Post Sprint 3): ✅ Issue #47 fix (indexed equations)
- **v0.4.0** (Sprint 4): ✅ Extended features and robustness
- **v1.0.0** (Sprint 5): ✅ Production-ready with hardening, packaging, and comprehensive documentation

**Epic 2 — Parser coverage + simplification (Sprints 6-12):** ✅ COMPLETE — Parser coverage to 100% on the 28-fixture set; aggressive simplification with 26.19% term reduction; full CI infrastructure.

**Epic 3 — GAMSLIB testing infrastructure (Sprints 13-17):** ✅ COMPLETE — Pipeline runner (`scripts/gamslib/run_full_test.py`), automated reporting, schema-versioned status JSON, **v1.1.0 release**.

**Epic 4 — GAMSLIB corpus pipeline (Sprints 18-28):** 🔄 IN PROGRESS through Sprint 25.
- ✅ **Sprints 18-25 complete** — Parse 142/142 (100%), Translate 133/142 (93.7%), Solve 104 (78.2% of translated), Match 60 (42.3% of in-scope), 4,735 tests passing
- 🔄 **Sprint 26** (planned) — Pattern C gate generalization (#1354/#1355/#1356/#1357), Pattern A cohort reclassification, AD residuals (#1334/#1335). Targets: Match ≥45% (≥64), Solve Rate ≥81%, path_syntax_error ≤6.
- 🔄 **Sprints 27-28** — Solver consultation, performance benchmarks, **v2.0.0 release**.

For the Rolling KPIs table tracking per-sprint actuals + revised targets, see [docs/planning/EPIC_4/PROJECT_PLAN.md](docs/planning/EPIC_4/PROJECT_PLAN.md) §"Rolling KPIs & Tracking".

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
