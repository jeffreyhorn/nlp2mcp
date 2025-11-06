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

### Current (Sprint 1-4 Complete)

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
- Tests: a comprehensive test suite is provided. Run `./scripts/test_all.sh` or `pytest` to show current counts; the README avoids hard-coding counts to prevent drift.

**Sprint 4: Extended Features & Robustness** ✅ **COMPLETE**

- ✅ Day 1: `$include` and Preprocessing
- ✅ Day 2: `Table` Data Blocks
- ✅ Day 3: `min/max` Reformulation - Part 1 (Infrastructure)
- ✅ Day 4: `min/max` Reformulation - Part 2 (Implementation)
- ✅ Day 5: `abs(x)` Handling and Fixed Variables (`x.fx`)
- ✅ Day 6: Scaling Implementation + Developer Ergonomics Part 1
- ✅ Day 7: Diagnostics + Developer Ergonomics Part 2
- ✅ Day 8: PATH Solver Validation and Testing
- ✅ Day 9: Integration Testing, Documentation, and Examples
- ✅ Day 10: Polish, Buffer, and Sprint Wrap-Up

### Planned (See [docs/planning/PROJECT_PLAN.md](docs/planning/PROJECT_PLAN.md))

- 📋 Sprint 5: Packaging, documentation, and ecosystem integration (in progress)

## Installation

### Requirements

- Python 3.12 or higher (see `pyproject.toml` for the authoritative requirement)
- pip 21.3 or higher (recommended for editable installs and modern pyproject support)

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

If the package is published on PyPI, you can install it with:

```bash
pip install nlp2mcp
```

If not published (or to install directly from this repository), use one of the following:

```bash
# Local editable development install (recommended for contributors)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

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

After an editable install (`pip install -e .`) the package imports use the package name. Example usage:

```python
from nlp2mcp.ir.parser import parse_model_file
from nlp2mcp.ir.normalize import normalize_model
from nlp2mcp.ad.gradient import compute_objective_gradient
from nlp2mcp.ad.constraint_jacobian import compute_constraint_jacobian
from nlp2mcp.kkt.assemble import assemble_kkt_system
from nlp2mcp.emit.emit_gams import emit_gams_mcp

# Full pipeline
model = parse_model_file("examples/simple_nlp.gms")
normalize_model(model)
gradient = compute_objective_gradient(model)
J_eq, J_ineq = compute_constraint_jacobian(model)
kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
gams_code = emit_gams_mcp(kkt, model_name="mcp_model", add_comments=True)

print(gams_code)
```

Note: if you prefer running from the repository without installing, either set `PYTHONPATH=.`, or run modules directly (for example `python -m src.cli ...`), but the recommended workflow for development is an editable install so imports use `nlp2mcp.*`.

## Project Structure

The project layout below is a generated snapshot of the repository root (captured with `find` on Nov 5, 2025). It may still change; use the repository as the single source of truth.

```
nlp2mcp/
src
src/config_loader.py
src/config.py
src/logging_config.py
src/ad
src/ad/jacobian.py
src/ad/ad_core.py
src/ad/derivative_rules.py
src/ad/gradient.py
src/ad/__init__.py
src/ad/__pycache__
src/ad/__pycache__/api.cpython-312.pyc
src/ad/__pycache__/evaluator.cpython-312.pyc
src/ad/__pycache__/sparsity.cpython-312.pyc
src/ad/__pycache__/term_collection.cpython-312.pyc
src/ad/__pycache__/index_mapping.cpython-312.pyc
src/ad/__pycache__/constraint_jacobian.cpython-312.pyc
src/ad/__pycache__/jacobian.cpython-312.pyc
src/ad/__pycache__/validation.cpython-312.pyc
src/ad/__pycache__/derivative_rules.cpython-312.pyc
src/ad/__pycache__/gradient.cpython-312.pyc
src/ad/__pycache__/__init__.cpython-312.pyc
src/ad/sparsity.py
src/ad/api.py
src/ad/index_mapping.py
src/ad/constraint_jacobian.py
src/ad/term_collection.py
src/ad/evaluator.py
src/ad/validation.py
src/ir
src/ir/normalize.py
src/ir/model_ir.py
src/ir/__init__.py
src/ir/preprocessor.py
src/ir/__pycache__
src/ir/__pycache__/preprocessor.cpython-312.pyc
src/ir/__pycache__/symbols.cpython-312.pyc
src/ir/__pycache__/normalize.cpython-312.pyc
src/ir/__pycache__/model_ir.cpython-312.pyc
src/ir/__pycache__/__init__.cpython-312.pyc
src/ir/__pycache__/ast.cpython-312.pyc
src/ir/__pycache__/parser.cpython-312.pyc
src/ir/parser.py
src/ir/symbols.py
src/ir/ast.py
src/__init__.py
src/utils
src/utils/__init__.py
src/utils/__pycache__
src/utils/__pycache__/errors.cpython-312.pyc
src/utils/__pycache__/__init__.cpython-312.pyc
src/utils/errors.py
src/__pycache__
src/__pycache__/config.cpython-312.pyc
src/__pycache__/cli.cpython-312.pyc
src/__pycache__/__init__.cpython-312.pyc
src/__pycache__/logging_config.cpython-312.pyc
src/kkt
src/kkt/scaling.py
src/kkt/objective.py
src/kkt/partition.py
src/kkt/stationarity.py
src/kkt/kkt_system.py
src/kkt/naming.py
src/kkt/reformulation.py
src/kkt/__init__.py
src/kkt/__pycache__
src/kkt/__pycache__/complementarity.cpython-312.pyc
src/kkt/__pycache__/assemble.cpython-312.pyc
src/kkt/__pycache__/stationarity.cpython-312.pyc
src/kkt/__pycache__/kkt_system.cpython-312.pyc
src/kkt/__pycache__/scaling.cpython-312.pyc
src/kkt/__pycache__/objective.cpython-312.pyc
src/kkt/__pycache__/naming.cpython-312.pyc
src/kkt/__pycache__/partition.cpython-312.pyc
src/kkt/__pycache__/__init__.cpython-312.pyc
src/kkt/__pycache__/reformulation.cpython-312.pyc
src/kkt/complementarity.py
src/kkt/assemble.py
src/cli.py
src/diagnostics
src/diagnostics/__init__.py
src/diagnostics/__pycache__
src/diagnostics/__pycache__/matrix_market.cpython-312.pyc
src/diagnostics/__pycache__/statistics.cpython-312.pyc
src/diagnostics/__pycache__/__init__.cpython-312.pyc
src/diagnostics/statistics.py
src/diagnostics/matrix_market.py
src/emit
src/emit/expr_to_gams.py
src/emit/emit_gams.py
src/emit/__init__.py
src/emit/original_symbols.py
src/emit/__pycache__
src/emit/__pycache__/templates.cpython-312.pyc
src/emit/__pycache__/equations.cpython-312.pyc
src/emit/__pycache__/expr_to_gams.cpython-312.pyc
src/emit/__pycache__/model.cpython-312.pyc
src/emit/__pycache__/original_symbols.cpython-312.pyc
src/emit/__pycache__/__init__.cpython-312.pyc
src/emit/__pycache__/emit_gams.cpython-312.pyc
src/emit/model.py
src/emit/templates.py
src/emit/equations.py
src/validation
src/validation/gams_check.py
src/validation/__init__.py
src/validation/__pycache__
src/validation/__pycache__/gams_check.cpython-312.pyc
src/validation/__pycache__/__init__.cpython-312.pyc
src/gams
src/gams/gams_grammar.lark
src/gams/__init__.py
src/gams/__pycache__
src/gams/__pycache__/__init__.cpython-312.pyc

tests
tests/research
tests/research/table_verification
tests/research/table_verification/test_sparse_table.gms
tests/research/table_verification/debug_ast.py
tests/research/table_verification/test_no_semicolon.gms
tests/research/table_verification/test_table_only.gms
tests/research/table_verification/test_table_2d_only.gms
tests/research/table_verification/test_table_with_text.gms
tests/research/table_verification/__pycache__
tests/research/table_verification/test_simple_table.gms
tests/research/table_verification/debug_token_positions.py
tests/research/table_verification/test_table_parsing.py
tests/research/relative_path_verification
tests/research/relative_path_verification/main_relative.gms
tests/research/relative_path_verification/main_nested.gms
tests/research/relative_path_verification/subdir
tests/research/relative_path_verification/shared
tests/research/relative_path_verification/__pycache__
tests/research/relative_path_verification/test_relative_paths.py
tests/research/relative_path_verification/main_parent.gms
tests/research/relative_path_verification/data
tests/research/abs_handling_verification
tests/research/abs_handling_verification/ABS_HANDLING_RESEARCH.md
tests/research/abs_handling_verification/example1_soft_abs_accuracy.md
tests/research/abs_handling_verification/GAMS_NLP_RESULTS.md
tests/research/abs_handling_verification/example3_mpec_reformulation.md
tests/research/abs_handling_verification/example5_python_nlp_softabs.py
tests/research/abs_handling_verification/example2_derivative_verification.md
tests/research/abs_handling_verification/example5_gams_nlp_softabs.gms
tests/research/abs_handling_verification/example4_approach_comparison.md
tests/research/abs_handling_verification/example5_nlp_demonstration.md
tests/research/abs_handling_verification/example5_gams_nlp_softabs.lst
tests/research/auxiliary_vars_indexmapping_verification
tests/research/auxiliary_vars_indexmapping_verification/test_auxiliary_vars_in_indexmapping.py
tests/research/auxiliary_vars_indexmapping_verification/__pycache__
tests/research/include_verification
tests/research/include_verification/circular_a.inc
tests/research/include_verification/circular_b.inc
tests/research/include_verification/test_missing.gms
tests/research/include_verification/test_quoted.gms
tests/research/include_verification/level3.inc
tests/research/include_verification/subdir
tests/research/include_verification/test_paths.gms
tests/research/include_verification/level2.inc
tests/research/include_verification/level1.inc
tests/research/include_verification/file with spaces.inc
tests/research/include_verification/test_include.gms
tests/research/include_verification/data.inc
tests/research/include_verification/test_circular.gms
tests/research/include_verification/test_nested.gms
tests/research/nested_include_verification
tests/research/nested_include_verification/circular_a.inc
tests/research/nested_include_verification/circular_b.inc
tests/research/nested_include_verification/main_nested.gms
tests/research/nested_include_verification/level3.inc
tests/research/nested_include_verification/level2.inc
tests/research/nested_include_verification/test_nested_includes.py
tests/research/nested_include_verification/main_circular.gms
tests/research/nested_include_verification/__pycache__
tests/research/nested_include_verification/level1.inc
tests/research/scaling_verification
tests/research/scaling_verification/__pycache__
tests/research/scaling_verification/test_curtis_reid_verification.py
tests/research/max_reformulation_verification
tests/research/max_reformulation_verification/example3_multi_argument.md
tests/research/max_reformulation_verification/MAX_REFORMULATION_RESEARCH.md
tests/research/max_reformulation_verification/example4_nested_max.md
tests/research/max_reformulation_verification/example1_simple_max.md
tests/research/max_reformulation_verification/example2_max_min_equivalence.md
tests/research/fixed_variable_verification
tests/research/fixed_variable_verification/test_parser.py
tests/research/fixed_variable_verification/test_indexed_fixed.gms
tests/research/fixed_variable_verification/test_kkt.py
tests/research/fixed_variable_verification/__pycache__
tests/research/fixed_variable_verification/test_fixed_scalar.gms
tests/research/fixed_variable_verification/test_indexed.py
tests/research/fixed_variable_verification/test_normalization.py
tests/research/min_reformulation_verification
tests/research/min_reformulation_verification/example1_simple_min.md
tests/research/min_reformulation_verification/example3_multi_argument.md
tests/research/min_reformulation_verification/example2_min_with_constants.md
tests/research/min_reformulation_verification/MIN_REFORMULATION_RESEARCH.md
tests/research/min_reformulation_verification/example4_nested_min.md
tests/research/long_line_verification
tests/research/long_line_verification/test_line_limits.gms
tests/research/long_line_verification/many_constraints.gms
tests/research/long_line_verification/test_long_stationarity.gms
tests/research/long_line_verification/large_model.gms
tests/research/long_line_verification/simple_many_constraints.gms
tests/research/long_line_verification/test_long_stationarity.lst
tests/research/long_line_verification/225a
tests/research/long_line_verification/test_line_limits.lst
tests/research/long_line_verification/large_model_simple.gms
tests/research/long_line_verification/.gitignore
tests/research/long_line_verification/test_continuation.lst
tests/research/long_line_verification/test_continuation.gms
tests/research/long_line_verification/LINE_LENGTH_RESEARCH.md
tests/research/long_line_verification/test_continuation.lst
tests/research/auxiliary_constraints_verification
tests/research/auxiliary_constraints_verification/__pycache__
tests/research/auxiliary_constraints_verification/test_auxiliary_in_mcp.py
tests/research/include_modelir_verification
tests/research/include_modelir_verification/INCLUDE_PREPROCESSING_RESEARCH.md
tests/unit
tests/unit/ad
tests/unit/ad/test_ad_core.py
tests/unit/ad/test_simplify.py
tests/unit/ad/test_term_collection.py
tests/unit/ad/test_index_aware_diff.py
tests/unit/ad/test_trigonometric.py
tests/unit/ad/__pycache__
tests/unit/ad/test_unsupported.py
tests/unit/ad/test_abs_smoothing.py
tests/unit/ad/test_apply_simplification.py
tests/unit/ad/test_transcendental.py
tests/unit/ad/test_alias_resolution.py
tests/unit/ad/test_multiplicative_cancellation.py
tests/unit/ad/test_index_mapping.py
tests/unit/ad/test_power_simplification.py
tests/unit/ad/test_sum_aggregation.py
tests/unit/ad/test_sparsity.py
tests/unit/ad/test_arithmetic.py
tests/unit/ir
tests/unit/ir/__pycache__
tests/unit/ir/test_preprocessor.py
tests/unit/ir/test_table_parsing.py
tests/unit/ir/test_normalize.py
tests/unit/utils
tests/unit/utils/test_errors.py
tests/unit/utils/__init__.py
tests/unit/utils/__pycache__
tests/unit/__pycache__
tests/unit/__pycache__/test_config.cpython-312-pytest-8.4.2.pyc
tests/unit/kkt
tests/unit/kkt/test_scaling.py
tests/unit/kkt/__init__.py
tests/unit/kkt/test_reformulation.py
tests/unit/kkt/__pycache__
tests/unit/kkt/test_partition.py
tests/unit/kkt/test_objective.py
tests/unit/kkt/test_naming.py
tests/unit/test_config.py
tests/unit/diagnostics
tests/unit/diagnostics/test_statistics.py
tests/unit/diagnostics/__pycache__
tests/unit/diagnostics/test_matrix_market.py
tests/unit/emit
tests/unit/emit/test_templates.py
tests/unit/emit/__init__.py
tests/unit/emit/test_equations.py
tests/unit/emit/__pycache__
tests/unit/emit/test_expr_to_gams.py
tests/unit/emit/test_original_symbols.py
tests/unit/emit/test_variable_kinds.py
tests/unit/gams
tests/unit/gams/test_parser.py
tests/unit/gams/__pycache__
tests/conftest.py
tests/ad
tests/ir
tests/ir/__init__.py
tests/integration
tests/integration/ad
tests/integration/ad/test_gradient.py
tests/integration/ad/test_jacobian_structure.py
tests/integration/ad/test_evaluator.py
tests/integration/ad/__pycache__
tests/integration/ad/test_bound_jacobian.py
tests/integration/ad/test_constraint_jacobian.py
tests/integration/__pycache__
tests/integration/__pycache__/test_cli.cpython-312-pytest-8.4.2.pyc
tests/integration/__pycache__/test_api_contracts.cpython-312-pytest-8.4.2.pyc
tests/integration/kkt
tests/integration/kkt/__init__.py
tests/integration/kkt/__pycache__
tests/integration/kkt/test_kkt_full.py
tests/integration/kkt/test_stationarity.py
tests/integration/test_api_contracts.py
tests/integration/emit
tests/integration/emit/test_emit_full.py
tests/integration/emit/__pycache__
tests/integration/test_cli.py
tests/integration/gams_ir
tests/edge_cases
tests/edge_cases/__init__.py
tests/edge_cases/__pycache__
tests/edge_cases/__pycache__/test_edge_cases.cpython-312-pytest-8.4.2.pyc
tests/edge_cases/test_edge_cases.py
tests/golden
tests/golden/scalar_nlp_mcp.gms
tests/golden/simple_nlp_mcp.gms
tests/golden/indexed_balance_mcp.gms
tests/golden/min_max_test_mcp.gms
tests/golden/min_max_test_mcp_new.gms
tests/__init__.py
tests/__pycache__
tests/__pycache__/conftest.cpython-312-pytest-8.4.2.pyc
tests/__pycache__/__init__.cpython-312.pyc
tests/benchmarks
tests/benchmarks/__init__.py
tests/benchmarks/__pycache__
tests/benchmarks/__pycache__/test_performance.cpython-312-pytest-8.4.2.pyc
tests/benchmarks/test_performance.py
tests/e2e
tests/e2e/__pycache__
tests/e2e/__pycache__/test_integration.cpython-312-pytest-8.4.2.pyc
tests/e2e/__pycache__/test_golden.cpython-312-pytest-8.4.2.pyc
tests/e2e/__pycache__/test_smoke.cpython-312-pytest-8.4.2.pyc
tests/e2e/test_smoke.py
tests/e2e/test_integration.py
tests/e2e/test_golden.py
tests/validation
tests/validation/test_path_solver_minmax.py
tests/validation/test_path_solver.py
tests/validation/test_finite_difference.py
tests/validation/__pycache__
tests/validation/__pycache__/test_gams_check.cpython-312-pytest-8.4.2.pyc
tests/validation/__pycache__/test_finite_difference.cpython-312-pytest-8.4.2.pyc
tests/validation/__pycache__/test_path_solver.cpython-312-pytest-8.4.2.pyc
tests/validation/__pycache__/test_path_solver_minmax.cpython-312-pytest-8.4.2.pyc
tests/validation/test_gams_check.py
tests/gams
tests/gams/__init__.py

examples
examples/scalar_nlp.lst
examples/simple_nlp.gms
examples/min_max_test.gms
examples/sprint4_abs_portfolio.gms
examples/sprint4_fixed_vars_design.gms
examples/sprint4_comprehensive.gms
examples/scalar_nlp.gms
examples/fixed_var_test.gms
examples/sprint4_comprehensive_data.gms
examples/abs_test.gms
examples/indexed_balance.gms
examples/sprint4_minmax_production.gms
examples/sprint4_scaling_illconditioned.gms

docs
docs/research
docs/research/RESEARCH_SUMMARY_TABLE_SYNTAX.md
docs/research/minmax_objective_reformulation.md
docs/research/RESEARCH_SUMMARY_FIXED_VARIABLES.md
docs/research/convexity_detection.md
docs/USER_GUIDE.md
docs/ad
docs/ad/ARCHITECTURE.md
docs/ad/README.md
docs/ad/DESIGN.md
docs/ad/DERIVATIVE_RULES.md
docs/ir
docs/ir/parser_output_reference.md
docs/DAY_8_COMPLETION_SUMMARY.md
docs/development
docs/development/ERROR_MESSAGES.md
docs/development/AGENTS.md
docs/planning
docs/planning/SPRINT_1
docs/planning/PROJECT_PLAN.md
docs/planning/README.md
docs/planning/SPRINT_2
docs/planning/SPRINT_5
docs/planning/SPRINT_4
docs/planning/SPRINT_3
docs/kkt
docs/kkt/KKT_ASSEMBLY.md
docs/testing
docs/testing/TEST_PYRAMID.md
docs/testing/EDGE_CASE_MATRIX.md
docs/architecture
docs/architecture/DATA_STRUCTURES.md
docs/architecture/SYSTEM_ARCHITECTURE.md
docs/concepts
docs/concepts/IDEA.md
docs/concepts/NLP2MCP_HIGH_LEVEL.md
docs/emit
docs/emit/GAMS_EMISSION.md
docs/issues
docs/issues/completed
docs/issues/minmax-reformulation-spurious-variables.md
docs/PATH_REQUIREMENTS.md
docs/migration
docs/migration/index_aware_differentiation.md
docs/process
docs/process/CHECKPOINT_TEMPLATES.md

CHANGELOG.md
CONTRIBUTING.md
docs
examples
Makefile
pyproject.toml
README.md
requirements.txt
scripts
setup.py
src
tests
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

## Test Organization

The test suite is split into unit, integration, e2e, and validation layers. You can run the different subsets with the scripts in `./scripts/` or via pytest directly. Below are the counts collected locally on Nov 5, 2025 (run in this repository with `python3 -m pytest --collect-only`):

- Total collected tests: **1281**
- Marker breakdown (may overlap if tests carry multiple markers):
  - unit: **434**
  - integration: **223**
  - e2e: **45**
  - validation: **66**

Note: marker-based counts can overlap and the total may include tests without markers or additional collected items (fixtures, doctests, etc.). To reproduce these numbers locally run:

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

### Preprocessing
- ✅ `$include` directive (nested, relative paths)

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
- ✅ `min()` and `max()` (reformulated to complementarity)
- ✅ `abs()` (smooth approximation with `--smooth-abs`)

### Equations
- ✅ Relations: `=e=` (equality), `=l=` (≤), `=g=` (≥)
- ✅ Variable bounds: `.lo`, `.up`, `.fx`

### Model
- ✅ `Model` declaration with equation lists or `/all/`
- ✅ `Solve` statement with `using NLP` and objective

### Advanced Features
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

This project is in active development (Sprint 4 complete, Sprint 5 in preparation). Contributions are welcome!

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
- **v0.4.0** (Sprint 4):✅ Extended features and robustness - COMPLETE
- **v1.0.0** (Sprint 5): 🔄 Production-ready with docs and PyPI release - IN PROGRESS

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
