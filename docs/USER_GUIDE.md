# nlp2mcp User Guide

**Transform GAMS NLP models to MCP format via KKT conditions**

Version: 0.4.0 (Sprint 4)  
Last Updated: 2025-11-02

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Basic Usage](#basic-usage)
5. [Sprint 4 Features](#sprint-4-features)
6. [Command-Line Options](#command-line-options)
7. [Configuration](#configuration)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Topics](#advanced-topics)

---

## Introduction

### What is nlp2mcp?

`nlp2mcp` automatically transforms nonlinear programming (NLP) models written in GAMS into Mixed Complementarity Problem (MCP) format by deriving the Karush-Kuhn-Tucker (KKT) optimality conditions.

### When to use nlp2mcp?

Use nlp2mcp when you:
- Want to solve NLP problems using complementarity solvers (e.g., PATH)
- Need to analyze the KKT system structure
- Want to verify first-order optimality conditions
- Need to work with equilibrium problems

### How it works

```
GAMS NLP Model
      ↓
  [Parse & Normalize]
      ↓
  [Compute Derivatives]
      ↓
  [Assemble KKT System]
      ↓
  [Generate GAMS MCP]
```

The KKT system includes:
- **Stationarity equations**: ∇f + J^T λ - π^L + π^U = 0
- **Complementarity conditions**: g(x) ⊥ λ, bounds ⊥ π
- **Multipliers**: Dual variables for constraints and bounds

---

## Installation

### Requirements

- Python 3.12 or later
- pip package manager

### Install from source

```bash
git clone https://github.com/yourusername/nlp2mcp.git
cd nlp2mcp
pip install -e .
```

### Verify installation

```bash
nlp2mcp --help
```

---

## Quick Start

### 1. Create a simple NLP model

Save this as `simple.gms`:

```gams
Variables x, y, obj;

Equations
    objective  Define objective
    constraint Constraint equation
;

objective..  obj =E= sqr(x - 2) + sqr(y - 3);
constraint.. x + y =E= 5;

x.lo = 0; y.lo = 0;

Model simple /all/;
Solve simple using NLP minimizing obj;
```

### 2. Convert to MCP

```bash
nlp2mcp simple.gms -o simple_mcp.gms
```

### 3. View the output

The generated `simple_mcp.gms` contains:
- Stationarity equations for x and y
- Multiplier variable for the constraint
- MCP model statement pairing equations with variables

### 4. Solve with PATH

The generated MCP can be solved directly with the PATH solver in GAMS:

```bash
# Solve the MCP with PATH
gams simple_mcp.gms
```

**PATH is the recommended MCP solver** for nlp2mcp-generated models. Default options work well for most cases.

For detailed PATH solver guidance, troubleshooting, and option tuning, see:
📖 **[PATH Solver Guide](PATH_SOLVER.md)**

The guide covers:
- PATH solver options reference
- Configuration templates for different problem types
- Troubleshooting decision tree
- Interpreting PATH output and diagnostics

---

## Basic Usage

### Input/Output

```bash
# Write to file
nlp2mcp input.gms -o output.gms

# Write to stdout
nlp2mcp input.gms

# Pipe to another command
nlp2mcp input.gms | less
```

### Verbosity Control

```bash
# Normal output (default)
nlp2mcp input.gms -o output.gms

# Verbose (show pipeline stages)
nlp2mcp input.gms -o output.gms -v

# Very verbose (show detailed info)
nlp2mcp input.gms -o output.gms -vv

# Quiet (errors only)
nlp2mcp input.gms -o output.gms --quiet
```

### Model Customization

```bash
# Custom model name
nlp2mcp input.gms -o output.gms --model-name my_model

# Without comments
nlp2mcp input.gms -o output.gms --no-comments

# Show excluded bounds
nlp2mcp input.gms -o output.gms --show-excluded
```

### Comment Handling

**Your input files can contain comments** - you don't need to strip them!

nlp2mcp supports all three GAMS comment styles:

```gams
* GAMS inline comment (line starting with asterisk)
x.lo = 0;  * Lower bound comment

// C-style line comment
y.up = 100;  // Upper bound

$ontext
Block comment spanning
multiple lines - useful for
documentation sections
$offtext
```

**Important notes:**
- ✅ All comment types are handled correctly during parsing
- ❌ Input comments are **not** preserved in the output file (they are stripped)
- ℹ️ Output files can optionally include **generated** explanatory comments about the KKT system structure (use `--no-comments` to disable)

**Example:**

```bash
# Input file with comments → Output without input comments
nlp2mcp model_with_comments.gms -o output.gms

# Disable generated explanatory comments in output
nlp2mcp model_with_comments.gms -o output.gms --no-comments
```

---

## Sprint 4 Features

### 1. File Inclusion ($include)

Organize your model into multiple files:

**main.gms:**
```gams
$include data.gms
$include equations.gms

Model mymodel /all/;
Solve mymodel using NLP minimizing obj;
```

**Features:**
- Nested includes supported
- Relative paths (relative to containing file)
- Circular include detection
- Clear error messages with source locations

**Usage:**
```bash
nlp2mcp main.gms -o output.gms
```

### 2. Table Data Blocks

Define parameters using tables:

```gams
Table demand(t) Product demand by period
       t1   t2   t3   t4
  prod 100  120  150  130
;

Table costs(i,j) Shipping costs
         dest1  dest2  dest3
  orig1    5      8      12
  orig2    7      6      10
  orig3    9      11     8
;
```

**Features:**
- 2D tables with row and column headers
- Sparse tables (missing values treated as zero)
- Descriptive text support

### 3. min/max Reformulation

Use `min()` and `max()` in expressions:

```gams
* Minimize worst-case shortage
objective.. obj =E= max(shortage1, shortage2, shortage3);

* Minimum production constraint
constraint.. production =G= min(demand, capacity);
```

**How it works:**
- `min(x,y)` → auxiliary variable z with complementarity constraints
- `max(x,y)` → similar reformulation with reversed inequalities
- Multi-argument: `min(a,b,c)` supported
- Nested: `min(min(x,y),z)` flattened automatically

**No special flags needed** - reformulation is automatic.

### 4. abs() Handling

Handle absolute value functions:

```gams
* Minimize total deviation
objective.. obj =E= sum(i, abs(x(i) - target(i)));
```

**Requirements:**
- Use `--smooth-abs` flag to enable
- Uses smooth approximation: `abs(x) ≈ sqrt(x² + ε)`
- Default ε = 1e-6 (max error ~0.001 at x=0)

**Usage:**
```bash
nlp2mcp model.gms -o output.gms --smooth-abs

# Custom epsilon
nlp2mcp model.gms -o output.gms --smooth-abs --smooth-abs-epsilon 1e-8
```

**Accuracy:**
- Excellent for |x| ≥ 0.1 (relative error < 0.1%)
- Small error near x=0 (bounded by ε)
- Continuous derivative everywhere

### 5. Fixed Variables (x.fx)

Fix variables to specific values:

```gams
Variables x, y, z;

* Fix x to 10
x.fx = 10;

* Fix indexed variable
production.fx('t1') = 100;
```

**How it works:**
- Creates equality constraint: `x - 10 = 0`
- Paired with free multiplier in MCP
- No stationarity equation for fixed variables
- Dimension balance maintained

### 6. Scaling

Improve conditioning for ill-scaled problems:

```bash
# Curtis-Reid scaling (row/column norm balancing)
nlp2mcp model.gms -o output.gms --scale auto

# Per-variable scaling
nlp2mcp model.gms -o output.gms --scale byvar

# No scaling (default)
nlp2mcp model.gms -o output.gms --scale none
```

**When to use:**
- Variables/constraints have vastly different magnitudes (e.g., 1e-6 to 1e6)
- Solver reports numerical issues
- KKT matrix is ill-conditioned

**Scaling modes:**
- `auto`: Curtis-Reid iterative row/column scaling
- `byvar`: Scale each variable's column independently
- `none`: No scaling (default)

### 7. Diagnostics

#### Model Statistics

```bash
nlp2mcp model.gms -o output.gms --stats
```

**Output:**
```
Model Statistics:
------------------
Equations:
  Stationarity:           10
  Complementarity (ineq):  5
  Complementarity (lo):    3
  Complementarity (up):    2
  Total:                  20

Variables:
  Primal:                 10
  Multipliers (eq):        0
  Multipliers (ineq):      5
  Multipliers (bounds):    5
  Total:                  20

Jacobian:
  Nonzeros:              85
  Density:              21.3%
```

#### Jacobian Export

```bash
nlp2mcp model.gms -o output.gms --dump-jacobian jac.mtx
```

Exports Jacobian structure in Matrix Market format for:
- Analysis with SciPy/MATLAB
- Visualization of sparsity pattern
- Conditioning analysis
- Debugging

---

## Command-Line Options

### Complete Reference

```
Usage: nlp2mcp [OPTIONS] INPUT_FILE

Arguments:
  INPUT_FILE  Input GAMS NLP file

Options:
  -o, --output PATH              Output file (default: stdout)
  -v, --verbose                  Increase verbosity (-v, -vv, -vvv)
  -q, --quiet                    Suppress non-error output
  --model-name TEXT              MCP model name (default: mcp_model)
  --show-excluded / --no-show-excluded
                                 Show excluded bounds (default: no)
  --no-comments                  Disable comments in output
  --stats                        Print model statistics
  --dump-jacobian PATH           Export Jacobian to Matrix Market format
  --scale {none,auto,byvar}      Scaling mode (default: none)
  --simplification {none,basic,advanced}
                                 Expression simplification (default: advanced)
  --smooth-abs                   Enable abs() smoothing
  --smooth-abs-epsilon FLOAT     Epsilon for abs smoothing (default: 1e-6)
  --help                         Show this message and exit
```

### Flag Interactions

- `--quiet` overrides `--verbose`
- `--stats` respects verbosity settings
- `--smooth-abs` required for models with `abs()`
- `--scale` is opt-in (default: none)

---

## Configuration

### pyproject.toml

Set project-wide defaults:

```toml
[tool.nlp2mcp]
model_name = "my_mcp_model"
add_comments = true
show_excluded_bounds = false
verbosity = 1                    # 0=quiet, 1=normal, 2=verbose
smooth_abs = false
smooth_abs_epsilon = 1e-6
scale = "none"                   # none, auto, or byvar
print_stats = false
```

**Precedence:** CLI flags > pyproject.toml > defaults

**Location:** Current directory or parent directories

---

## Examples

### Example 1: Production Planning with min/max

See `examples/sprint4_minmax_production.gms`

**Features:**
- `max()` in objective (penalize worst shortage)
- `min()` in constraints (minimum production)
- Multi-argument max()

**Run:**
```bash
nlp2mcp examples/sprint4_minmax_production.gms -o output.gms --stats
```

### Example 2: Portfolio with abs() Smoothing

See `examples/sprint4_abs_portfolio.gms`

**Features:**
- `abs()` for deviation minimization
- Requires `--smooth-abs` flag

**Run:**
```bash
nlp2mcp examples/sprint4_abs_portfolio.gms -o output.gms --smooth-abs
```

### Example 3: Engineering Design with Fixed Variables

See `examples/sprint4_fixed_vars_design.gms`

**Features:**
- Fixed variables (`x.fx = value`)
- Mixed fixed/free optimization

**Run:**
```bash
nlp2mcp examples/sprint4_fixed_vars_design.gms -o output.gms
```

### Example 4: Ill-Conditioned System with Scaling

See `examples/sprint4_scaling_illconditioned.gms`

**Features:**
- Large magnitude differences (1e-6 to 1e6)
- Demonstrates scaling improvement

**Run:**
```bash
# Without scaling
nlp2mcp examples/sprint4_scaling_illconditioned.gms -o output_unscaled.gms

# With Curtis-Reid scaling
nlp2mcp examples/sprint4_scaling_illconditioned.gms -o output_scaled.gms --scale auto
```

### Example 5: Comprehensive (All Features)

See `examples/sprint4_comprehensive.gms`

**Features:**
- `$include` directive
- `Table` data blocks
- `min()` and `max()` functions
- Fixed variables
- Scaling recommendation

**Run:**
```bash
nlp2mcp examples/sprint4_comprehensive.gms -o output.gms --scale auto --stats
```

---

## Troubleshooting

### Common Issues

#### "abs() not supported without --smooth-abs"

**Problem:** Model uses `abs()` but flag not provided.

**Solution:**
```bash
nlp2mcp model.gms -o output.gms --smooth-abs
```

**Note:** Review accuracy requirements (max error ~ε at x=0).

#### "Circular include detected"

**Problem:** Files include each other in a loop.

**Solution:** Restructure to avoid circular dependencies:
- Use a main file that includes sub-files
- Don't have sub-files include the main file

#### "Model has no objective function"

**Problem:** Missing or unrecognized `Solve` statement.

**Solution:** Ensure model has:
```gams
Model mymodel /all/;
Solve mymodel using NLP minimizing obj;  # or maximizing
```

#### Type errors or lint failures

**Problem:** Code quality checks failing.

**Solution:**
```bash
make typecheck  # Fix type errors
make lint       # Fix linting issues
make format     # Auto-format code
```

### Performance Issues

#### Large models slow to process

**Symptoms:** Long processing time, high memory usage.

**Solutions:**
1. Check model size with `--stats`
2. Verify sparsity with `--dump-jacobian` and analyze
3. Consider model decomposition
4. Use `--quiet` to reduce I/O overhead

#### Ill-conditioned warnings

**Symptoms:** Numerical warnings, poor convergence.

**Solutions:**
1. Try `--scale auto` for automatic scaling
2. Use `--stats` to check condition number (if available)
3. Review variable/constraint magnitudes
4. Consider rescaling problem manually

---

## Advanced Topics

### Expression Simplification

nlp2mcp automatically simplifies derivative expressions to produce cleaner, more readable output. The level of simplification can be controlled via the `--simplification` flag or configuration file.

#### Simplification Modes

**Advanced (default)** - `--simplification advanced`

Applies all basic simplifications plus algebraic term collection:

**Additive Term Collection** (for addition/subtraction):

1. **Constant Collection:**
   - `1 + x + 1` → `x + 2`
   - `3 + a + 5` → `a + 8`

2. **Like-Term Collection:**
   - `x + y + x + y` → `2*x + 2*y`
   - `a(i) + b(i) + a(i)` → `2*a(i) + b(i)`

3. **Coefficient Collection:**
   - `2*x + 3*x` → `5*x`
   - `4*y - 2*y` → `2*y`

4. **Term Cancellation:**
   - `x - x` → `0`
   - `x + y - x` → `y`
   - `3*a - 3*a` → `0`

5. **Complex Bases:**
   - `x*y + 2*x*y` → `3*x*y`
   - `a(i)*b(j) + a(i)*b(j)` → `2*a(i)*b(j)`

**Multiplicative Term Collection** (for multiplication):

6. **Variable Collection:**
   - `x * x` → `x^2`
   - `x * x * x` → `x^3`
   - Works recursively: `(x * x) * x` → `x^2 * x` → `x^3`

7. **Power Multiplication:**
   - `x^2 * x^3` → `x^5`
   - `x(i)^2 * x(i)^3` → `x(i)^5` (indexed variables)
   - `x^a * x^b` → `x^(a+b)` (general rule)

8. **Mixed Multiplication:**
   - `x^2 * x` → `x^3`
   - `x * x^2` → `x^3`
   - `x^(-2) * x^3` → `x`

**Other Algebraic Rules:**

9. **Multiplicative Cancellation:**
   - `2*x / 2` → `x`
   - `x*3 / 3` → `x`
   - `2*x / (1+1)` → `x` (after constant folding)
   - `3*(x+y) / 3` → `x+y`

10. **Power Division:**
   - `x^5 / x^2` → `x^3`
   - `x / x^2` → `1/x`
   - `x^2 / x^5` → `1/x^3` (negative exponent result)
   - `x^a / x^b` → `x^(a-b)` (general rule)

11. **Nested Powers:**
   - `(x^2)^3` → `x^6`
   - `(x^a)^b` → `x^(a*b)` (general rule)
   - `(x^0.5)^2` → `x`

Plus all basic simplifications (constant folding, zero/identity elimination).

**Basic** - `--simplification basic`

Applies only fundamental simplification rules:

1. **Constant Folding:**
   - `2 + 3` → `5`
   - `(1 + 1) * x` → `2 * x`
   - `4 * 5` → `20`

2. **Zero Elimination:**
   - `x + 0` → `x`
   - `x * 0` → `0`
   - `0 / x` → `0`
   - `0 - x` → `-x`

3. **Identity Elimination:**
   - `x * 1` → `x`
   - `x / 1` → `x`
   - `x ** 1` → `x`
   - `x ** 0` → `1`
   - `1 ** x` → `1`

4. **Algebraic Identities:**
   - `-(-x)` → `x` (double negation)
   - `x - x` → `0`
   - `x / x` → `1`

**None** - `--simplification none`

No simplification applied. Derivative expressions remain in raw differentiated form.

#### Usage Examples

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

Set the default simplification mode in `pyproject.toml`:

```toml
[tool.nlp2mcp]
simplification = "advanced"  # or "basic" or "none"
scale = "none"
smooth_abs = false
```

#### Example Impact

**Input derivative (before simplification):**
```gams
stat_x(i).. 1 + 0 + x(i) * 0 + a(i) * 1 + (1 - 0) * lam_balance(i) + lam_balance(i) =E= 0;
```

**With basic simplification:**
```gams
stat_x(i).. 1 + a(i) + lam_balance(i) + lam_balance(i) =E= 0;
```

**With advanced simplification:**
```gams
stat_x(i).. a(i) + 2*lam_balance(i) + 1 =E= 0;
```

Note: The constant terms remain on the left-hand side. GAMS equations are not automatically rearranged to move constants to the right-hand side.

#### When to Use Each Mode

- **Advanced** (default): Best for production use
  - Produces cleanest, most readable output
  - Reduces redundant terms in expressions
  - Recommended for all typical use cases

- **Basic**: When you need predictable transformations
  - Minimal transformation of expressions
  - Preserves expression structure more closely
  - Useful if you want to see differentiation pattern

- **None**: For debugging and education
  - See raw output of differentiation engine
  - Understand how chain rule is applied
  - Verify derivative computation manually
  - **Warning**: May produce very large expressions!

#### Technical Details

**Term-Based Collection (Advanced Mode):**

The advanced simplification uses a term collection algorithm:
1. Flatten nested additions into lists
2. Extract each term as (coefficient, base) pairs
3. Group terms by their base expression
4. Sum coefficients for like terms
5. Filter out zero terms
6. Rebuild optimized expression

This process is applied bottom-up through the expression tree, ensuring nested expressions are also optimized.

**Benefits:**
- Cleaner, more readable equations
- Smaller output files (fewer operators, shorter expressions)
- Potentially faster solver execution (fewer operations to evaluate)
- Easier manual verification of KKT conditions
- Better numerical properties (reduced cancellation errors)

### KKT System Structure

The generated MCP contains:

**1. Stationarity Equations** (one per variable):
```
stat_x.. ∇f + Σ J_i^T λ_i - π_lo + π_up =E= 0
```

**2. Complementarity Conditions**:
- Equality constraints: `h(x) = 0` paired with free multipliers
- Inequality constraints: `g(x) ⊥ λ` (λ ≥ 0, g ≤ 0, g·λ = 0)
- Bounds: `(x - lo) ⊥ π_lo`, `(up - x) ⊥ π_up`

**3. Auxiliary Constraints** (from reformulations):
- min/max: Epigraph constraints with multipliers
- Fixed vars: Equality constraints

### Scaling Algorithm Details

**Curtis-Reid Scaling:**
1. Compute row norms: `r_i = sqrt(Σ_j J_{ij}²)`
2. Scale rows: `R_i = 1/r_i`
3. Compute column norms: `c_j = sqrt(Σ_i J_{ij}²)`
4. Scale columns: `C_j = 1/c_j`
5. Iterate until convergence (row/col norms ≈ 1)

**Byvar Scaling:**
- Scale each variable's column to unit norm
- Independent per-variable scaling
- Simpler than Curtis-Reid

### Matrix Market Format

Exported Jacobian uses coordinate format:
```
%%MatrixMarket matrix coordinate real general
% KKT Jacobian from nlp2mcp
M N NNZ
row1 col1 1.0
row2 col2 1.0
...
```

**Features:**
- 1-based indexing (MATLAB/SciPy compatible)
- Sparse (COO) format
- Symbolic structure (all nonzeros = 1.0)

**Loading in Python:**
```python
from scipy.io import mmread
J = mmread('jacobian.mtx')
```

### Reformulation Details

**min(x,y) Reformulation:**
```
Create: z_min, λ_x, λ_y

Constraints:
  x - z_min ≥ 0
  y - z_min ≥ 0

Complementarity:
  (x - z_min) ⊥ λ_x
  (y - z_min) ⊥ λ_y

Stationarity for z_min:
  ∂obj/∂z_min - λ_x - λ_y = 0
```

**max(x,y) Reformulation:**
Similar with reversed inequalities (z_max ≥ args).

**abs(x) Smoothing:**
```
abs(x) ≈ sqrt(x² + ε)

Derivative: x / sqrt(x² + ε)
```

Continuous, smooth approximation with bounded error.

---

## Getting Help

### Documentation

- **User Guide:** This document
- **Technical Docs:** `docs/` directory
- **API Reference:** `docs/ad/`, `docs/kkt/`, `docs/emit/`
- **Examples:** `examples/` directory

### Support

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share tips

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process

---

## Appendix: Supported GAMS Syntax

### Fully Supported

- Sets, Aliases, Parameters, Scalars, Variables, Equations
- Table data blocks
- $include directive
- Arithmetic operators: +, -, *, /, ^
- Functions: exp, log, sqrt, sin, cos, tan
- min, max (reformulated)
- abs (with --smooth-abs)
- sum aggregation
- Relations: =e=, =l=, =g=
- Bounds: .lo, .up, .fx
- Model and Solve statements

### Not Supported

- Control flow: Loop, If, While
- Other $ directives: $if, $set, $macro
- External functions
- Other non-smooth functions: floor, ceil, sign

---

**End of User Guide**

For the latest updates, see: https://github.com/yourusername/nlp2mcp
