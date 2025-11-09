# nlp2mcp Tutorial

**Learn to convert GAMS NLP models to MCP format step-by-step**

Version: 0.5.0-beta  
Last Updated: 2025-11-08

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [First Conversion](#first-conversion)
4. [Understanding the Output](#understanding-the-output)
5. [Common Patterns](#common-patterns)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

### What You'll Learn

This tutorial will teach you how to:
- Convert your first GAMS NLP model to MCP format
- Understand the generated KKT conditions
- Use advanced features like min/max reformulation
- Solve the generated MCP with PATH
- Troubleshoot common issues

### Prerequisites

- Basic understanding of optimization (NLP models)
- GAMS installed (optional, for running examples)
- Python 3.11+ installed
- Familiarity with command-line tools

### Time Required

- Quick start: 15 minutes
- Complete tutorial: 1-2 hours

---

## Installation

### Step 1: Install nlp2mcp

```bash
pip install nlp2mcp
```

### Step 2: Verify Installation

```bash
nlp2mcp --help
```

You should see the help message with available options.

### Step 3: Check Version

```bash
nlp2mcp --version
```

Expected output: `nlp2mcp version 0.5.0-beta`

---

## First Conversion

### Example 1: Simple Unconstrained Optimization

Let's start with the simplest possible NLP model: minimizing a quadratic function.

**Create a file `simple.gms`:**

```gams
Variables x, y, obj;

Equations
    objective  Define objective function
;

objective.. obj =E= sqr(x - 2) + sqr(y - 3);

x.lo = 0;
y.lo = 0;

Model simple /all/;
Solve simple using NLP minimizing obj;
```

**What this model does:**
- Minimizes `(x-2)² + (y-3)²`
- Variables `x` and `y` are constrained to be non-negative
- Optimal solution: `x* = 2, y* = 3` (at the center of the quadratic)

**Convert to MCP:**

```bash
nlp2mcp simple.gms -o simple_mcp.gms
```

**Output:**
```
Parsing GAMS model...
Validating model structure...
Validating parameters...
Computing derivatives...
Assembling KKT system...
Generating MCP code...
Success! MCP model written to simple_mcp.gms
```

Congratulations! You've converted your first NLP to MCP.

---

## Understanding the Output

### Generated MCP Structure

Open `simple_mcp.gms` to see the generated KKT system. The file contains:

**1. Variable Declarations**
```gams
Variables
    x
    y
    obj
    pi_lo_x     Multiplier for x lower bound
    pi_lo_y     Multiplier for y lower bound
;
```

**What's new:**
- Original variables: `x`, `y`, `obj`
- New multiplier variables: `pi_lo_x`, `pi_lo_y` (dual variables for bounds)

**2. Stationarity Equations**

These ensure the gradient is zero (optimality condition):

```gams
Equations
    stat_x      Stationarity for x
    stat_y      Stationarity for y
;

stat_x.. 2*(x - 2) - pi_lo_x =E= 0;
stat_y.. 2*(y - 3) - pi_lo_y =E= 0;
```

**What these mean:**
- `stat_x`: `∂f/∂x - π_lo = 0` → `2(x-2) = π_lo`
- `stat_y`: `∂f/∂y - π_lo = 0` → `2(y-3) = π_lo`

At the optimum, these gradients must equal zero (or be balanced by multipliers if at bounds).

**3. Complementarity Conditions**

These implement the bound constraints:

```gams
Equations
    compl_lo_x  Complementarity for x lower bound
    compl_lo_y  Complementarity for y lower bound
;

compl_lo_x.. x - 0 =G= 0;
compl_lo_y.. y - 0 =G= 0;
```

**What these mean:**
- `x ≥ 0` and `π_lo_x ≥ 0`
- If `x > 0`, then `π_lo_x = 0` (not at bound)
- If `x = 0`, then `π_lo_x ≥ 0` (at bound, pushing away)

**4. MCP Model Statement**

```gams
Model simple_mcp /
    stat_x.x
    stat_y.y
    compl_lo_x.pi_lo_x
    compl_lo_y.pi_lo_y
/;
```

**Pairing explanation:**
- `stat_x.x`: Stationarity equation determines `x`
- `stat_y.y`: Stationarity equation determines `y`
- `compl_lo_x.pi_lo_x`: Complementarity determines multiplier `pi_lo_x`
- `compl_lo_y.pi_lo_y`: Complementarity determines multiplier `pi_lo_y`

**5. Solve Statement**

```gams
Solve simple_mcp using MCP;
```

This solves the system with the PATH solver (or another MCP solver).

---

### Example 2: Constrained Optimization

Now let's add an equality constraint to make things more interesting.

**Create `constrained.gms`:**

```gams
Variables x, y, obj;

Equations
    objective   Define objective
    constraint  Equality constraint
;

objective..  obj =E= sqr(x - 2) + sqr(y - 3);
constraint.. x + y =E= 5;

x.lo = 0;
y.lo = 0;

Model constrained /all/;
Solve constrained using NLP minimizing obj;
```

**What's different:**
- Added constraint: `x + y = 5`
- Now we can't have both `x=2` and `y=3` (they must sum to 5)

**Convert:**

```bash
nlp2mcp constrained.gms -o constrained_mcp.gms
```

**Inspect the output** (`constrained_mcp.gms`):

**New multiplier variable:**
```gams
Variables
    ...
    nu_constraint  Multiplier for equality constraint
;
```

**Updated stationarity equations:**
```gams
stat_x.. 2*(x - 2) + nu_constraint - pi_lo_x =E= 0;
stat_y.. 2*(y - 3) + nu_constraint - pi_lo_y =E= 0;
```

**Notice:**
- `nu_constraint` appears in both stationarity equations
- Coefficient is `1` (derivative of `x+y` w.r.t. `x` and `y`)

**Constraint equation:**
```gams
Equations
    eq_constraint  Enforce x + y = 5
;

eq_constraint.. x + y =E= 5;
```

**MCP pairing:**
```gams
Model constrained_mcp /
    stat_x.x
    stat_y.y
    eq_constraint.nu_constraint  * New: constraint paired with multiplier
    compl_lo_x.pi_lo_x
    compl_lo_y.pi_lo_y
/;
```

**Key insight:**
- Equality constraints add multipliers
- Multipliers appear in stationarity equations
- MCP pairs each equation with one variable

---

##Common Patterns

### Pattern 1: Box Constraints

**Input:**
```gams
Variables x;

x.lo = 0;
x.up = 10;
```

**Generated MCP:**
```gams
Variables
    x
    pi_lo_x  Multiplier for lower bound
    pi_up_x  Multiplier for upper bound
;

Equations
    stat_x          Stationarity for x
    compl_lo_x      x >= 0 ⊥ pi_lo_x >= 0
    compl_up_x      10 >= x ⊥ pi_up_x >= 0
;

stat_x.. <gradient> - pi_lo_x + pi_up_x =E= 0;
compl_lo_x.. x - 0 =G= 0;
compl_up_x.. 10 - x =G= 0;
```

**Pattern:**
- Lower bound: `- pi_lo_x` (pushes x up)
- Upper bound: `+ pi_up_x` (pushes x down)
- Complementarity: `x-lo ⊥ pi_lo`, `up-x ⊥ pi_up`

### Pattern 2: Inequality Constraints

**Input:**
```gams
Equations
    ineq  Inequality constraint
;

ineq.. x + y =L= 10;
```

**Generated MCP:**
```gams
Variables
    lam_ineq  Multiplier for inequality
;

Equations
    compl_ineq  Complementarity for inequality
;

* In stationarity:
stat_x.. <grad> + lam_ineq - <bounds> =E= 0;
stat_y.. <grad> + lam_ineq - <bounds> =E= 0;

* Complementarity:
compl_ineq.. 10 - (x + y) =G= 0;
```

**MCP pairing:**
```gams
Model mcp /
    ...
    compl_ineq.lam_ineq  * Ineq paired with its multiplier
/;
```

**Pattern:**
- `=L=` becomes `≤` (RHS - LHS ≥ 0)
- Multiplier `lam` appears in stationarity
- Complementarity: `RHS-LHS ≥ 0 ⊥ lam ≥ 0`

### Pattern 3: Free Variables

**Input:**
```gams
Variables x;
* No bounds specified
```

**Generated MCP:**
```gams
Variables x;

Equations stat_x;

stat_x.. <gradient> =E= 0;

Model mcp /stat_x.x/;
```

**Pattern:**
- No multiplier variables for bounds
- Pure stationarity: gradient = 0
- Simplest case

### Pattern 4: Fixed Variables

**Input:**
```gams
Variables x;

x.fx = 5;
```

**Generated MCP:**
```gams
Variables
    x
    nu_fix_x  Multiplier for fixed value
;

Equations
    fix_x  Enforce fixed value
;

fix_x.. x - 5 =E= 0;

Model mcp /
    fix_x.nu_fix_x  * Fixed value paired with multiplier
/;
```

**Pattern:**
- Fixed variable gets equality constraint
- Multiplier is free (can be positive or negative)
- No stationarity equation for fixed variable

---

## Advanced Features

### Min/Max Reformulation

nlp2mcp automatically reformulates `min()` and `max()` functions using auxiliary variables and complementarity conditions.

**Example: Minimize worst-case shortage**

**Create `minmax.gms`:**

```gams
Variables x1, x2, x3, obj;

Equations
    objective  Minimize maximum shortage
;

objective.. obj =E= max(10 - x1, 10 - x2, 10 - x3);

x1.lo = 0; x1.up = 15;
x2.lo = 0; x2.up = 15;
x3.lo = 0; x3.up = 15;

Model minmax /all/;
Solve minmax using NLP minimizing obj;
```

**What this does:**
- Minimizes the maximum shortage among three items
- Ensures no item goes below 10 (penalty increases linearly below 10)

**Convert:**

```bash
nlp2mcp minmax.gms -o minmax_mcp.gms
```

**Generated reformulation:**

```gams
Variables
    aux_max_1  Auxiliary variable for max()
    lam_max_arg_1  Multiplier for first argument
    lam_max_arg_2  Multiplier for second argument
    lam_max_arg_3  Multiplier for third argument
;

Equations
    aux_max_def_1  Define aux as max of arguments
    aux_ineq_1_1   aux >= 10 - x1
    aux_ineq_1_2   aux >= 10 - x2
    aux_ineq_1_3   aux >= 10 - x3
;

aux_ineq_1_1.. aux_max_1 - (10 - x1) =G= 0;
aux_ineq_1_2.. aux_max_1 - (10 - x2) =G= 0;
aux_ineq_1_3.. aux_max_1 - (10 - x3) =G= 0;
```

**Stationarity for auxiliary:**

```gams
stat_aux_max_1.. 1 - lam_max_arg_1 - lam_max_arg_2 - lam_max_arg_3 =E= 0;
```

**Complementarity:**
```gams
* If aux > arg_i, then lam_i = 0 (not binding)
* If aux = arg_i, then lam_i > 0 (binding)
* Exactly one argument will be binding (the maximum)
```

**Key insight:**
- `max()` becomes: auxiliary variable ≥ all arguments
- Complementarity ensures aux equals the maximum argument
- Works automatically - no special syntax needed

### Smooth abs() Approximation

For models with absolute value functions, use the `--smooth-abs` flag.

**Example:**

**Create `abs_model.gms`:**

```gams
Variables x1, x2, obj;

Equations
    objective  Minimize total deviation
;

objective.. obj =E= abs(x1 - 5) + abs(x2 + 3);

Model abs_model /all/;
Solve abs_model using NLP minimizing obj;
```

**Convert with smoothing:**

```bash
nlp2mcp abs_model.gms -o abs_mcp.gms --smooth-abs
```

**Generated approximation:**

```gams
* abs(x) ≈ sqrt(x² + ε)  where ε = 1e-6

objective.. obj =E= sqrt(power(x1 - 5, 2) + 1e-6)
                  + sqrt(power(x2 + 3, 2) + 1e-6);
```

**Accuracy:**
- Excellent for |x| ≥ 0.1 (relative error < 0.1%)
- Small error near x=0 (absolute error ≤ ε)
- Continuous derivative everywhere (PATH can solve it)

**Tune epsilon if needed:**

```bash
nlp2mcp abs_model.gms -o abs_mcp.gms --smooth-abs --smooth-abs-epsilon 1e-8
```

Smaller epsilon = more accurate, but can cause numerical issues.

### File Inclusion

Organize large models using `$include`.

**Example:**

**File: `data.gms`**
```gams
Parameters
    demand(t)  Product demand by period
    /t1 100, t2 120, t3 150/;
```

**File: `equations.gms`**
```gams
Equations
    balance(t)  Inventory balance
;

balance(t).. production(t) + inventory(t-1) =E= demand(t) + inventory(t);
```

**File: `main.gms`**
```gams
$include data.gms
$include equations.gms

Model production_model /all/;
Solve production_model using NLP minimizing total_cost;
```

**Convert:**

```bash
nlp2mcp main.gms -o main_mcp.gms
```

nlp2mcp automatically resolves includes and processes the complete model.

### Scaling for Ill-Conditioned Models

If your model has variables/constraints with vastly different magnitudes, use scaling.

**Example:**

```gams
Variables
    x  "Quantity (units: thousands)"
    y  "Price (units: dollars)"
    obj;

* x ranges from 0 to 1000 (thousands)
* y ranges from 0.01 to 100 (dollars)
```

**Convert with auto-scaling:**

```bash
nlp2mcp model.gms -o model_mcp.gms --scale auto
```

**What it does:**
- Curtis-Reid algorithm balances row/column norms
- Improves numerical conditioning
- Helps PATH convergence

**When to use:**
- Seeing PATH convergence issues
- Variables/constraints differ by 3+ orders of magnitude
- Getting numerical warnings

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Model has no objective function defined"

**Error message:**
```
ModelError: Model has no objective function defined
```

**Cause:** Missing or incorrectly formatted `Solve` statement.

**Solution:**
```gams
* Correct:
Model mymodel /all/;
Solve mymodel using NLP minimizing obj;  * Must specify minimizing/maximizing

* Incorrect:
Solve mymodel;  * Missing objective
```

#### Issue 2: "abs() not supported without --smooth-abs"

**Error message:**
```
Unsupported function 'abs' - use --smooth-abs flag
```

**Cause:** Model uses `abs()` but smoothing flag not provided.

**Solution:**
```bash
nlp2mcp model.gms -o output.gms --smooth-abs
```

**Note:** Review accuracy requirements before using smooth approximation.

#### Issue 3: PATH Model Status 5 (Locally Infeasible)

**Symptom:** Generated MCP solves with Model Status 5.

**Possible causes:**
1. Original NLP is infeasible
2. Model is non-convex (KKT conditions may not be sufficient)
3. Poor scaling
4. Bad initial point

**Solutions:**

**Step 1: Verify original NLP solves**
```bash
# Solve original with CONOPT
gams original.gms
# Check if NLP finds feasible solution
```

**Step 2: Try scaling**
```bash
nlp2mcp model.gms -o output.gms --scale auto
```

**Step 3: Adjust PATH options**

Create `path.opt`:
```
convergence_tolerance 1e-4
major_iteration_limit 1000
crash_method none
```

See [PATH Solver Guide](PATH_SOLVER.md) for detailed tuning guidance.

#### Issue 4: Generated MCP is huge/slow

**Symptom:** Output file is very large, processing takes a long time.

**Solutions:**

**Check model size:**
```bash
nlp2mcp model.gms -o output.gms --stats
```

**Expected performance:**
- 250 variables: < 10 seconds
- 500 variables: < 30 seconds
- 1000 variables: < 90 seconds

**If slower:**
- Use `--quiet` to reduce I/O overhead
- Consider model decomposition
- Check for excessively complex expressions

#### Issue 5: NaN or Inf in results

**Error message:**
```
NumericalError: Parameter 'p[1]' has invalid value (value is NaN)
```

**Cause:** Invalid numerical values in input data or expressions.

**Solution:**

**Check parameters:**
```gams
* Ensure all parameters are initialized
Parameter p(i);
p(i) = 0;  * Initialize before use
```

**Check expressions:**
```gams
* Avoid:
obj =E= log(0);        * log(0) = -Inf
obj =E= sqrt(-1);      * sqrt(negative) = NaN
obj =E= 1 / 0;         * division by zero

* Use bounds to prevent:
x.lo = 0.001;  * Ensure x > 0 for log(x)
```

---

## Next Steps

### Further Reading

- [User Guide](USER_GUIDE.md) - Complete reference for all features
- [PATH Solver Guide](PATH_SOLVER.md) - Detailed PATH solver configuration
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Comprehensive problem-solving reference
- [FAQ](FAQ.md) - Frequently asked questions

### Example Models

Explore the `examples/` directory for more models:
- `simple_nlp.gms` - Basic unconstrained optimization
- `indexed_balance.gms` - Model with indexed variables/equations
- `min_max_test.gms` - Min/max reformulation examples
- `abs_test.gms` - Absolute value handling
- `fixed_var_test.gms` - Fixed variable examples

### Getting Help

- GitHub Issues: https://github.com/jeffreyhorn/nlp2mcp/issues
- Discussions: https://github.com/jeffreyhorn/nlp2mcp/discussions

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Contributing code
- Improving documentation

---

**Congratulations!** You've completed the nlp2mcp tutorial. You now know how to convert NLP models to MCP format, understand the generated KKT conditions, and use advanced features.

Happy optimizing!
