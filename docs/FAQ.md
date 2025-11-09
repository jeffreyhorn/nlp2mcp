# nlp2mcp Frequently Asked Questions (FAQ)

**Common questions and answers about nlp2mcp**

Version: 0.5.0-beta  
Last Updated: 2025-11-08

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Basic Usage](#basic-usage)
3. [Conversion Process](#conversion-process)
4. [Advanced Features](#advanced-features)
5. [PATH Solver](#path-solver)
6. [Troubleshooting](#troubleshooting)
7. [Performance & Limitations](#performance--limitations)

---

## Installation & Setup

### Q1: What Python version do I need?

**A:** Python 3.11 or higher is required.

nlp2mcp requires NumPy 2.x, which only supports Python 3.11+. Check your Python version:

```bash
python --version
```

If you have Python 3.10 or earlier, upgrade to Python 3.11 or 3.12.

### Q2: Can I install nlp2mcp without pip?

**A:** Yes, you can install from source:

```bash
git clone https://github.com/jeffreyhorn/nlp2mcp.git
cd nlp2mcp
pip install -e .
```

This is useful for development or if you want the latest unreleased features.

### Q3: Do I need GAMS installed to use nlp2mcp?

**A:** No, nlp2mcp does not require GAMS to convert models.

However, you will need GAMS with the PATH solver to **solve** the generated MCP files. nlp2mcp only performs the NLP→MCP conversion; solving is done by GAMS/PATH.

### Q4: What operating systems are supported?

**A:** All major platforms: Linux, macOS, and Windows.

nlp2mcp is pure Python with no platform-specific code. The generated GAMS files are also platform-independent.

### Q5: How do I upgrade to the latest version?

**A:** Use pip to upgrade:

```bash
pip install --upgrade nlp2mcp
```

Check the new version:

```bash
nlp2mcp --version
```

---

## Basic Usage

### Q6: What file format does nlp2mcp accept?

**A:** nlp2mcp accepts GAMS (.gms) files containing NLP models.

The file must include:
- Variable declarations
- Equation declarations and definitions
- A Model statement
- A Solve statement specifying NLP and an objective

### Q7: Can I use nlp2mcp with models written in other languages (AMPL, Pyomo, JuMP)?

**A:** Not directly. nlp2mcp only parses GAMS syntax.

However, you can:
1. Manually translate your model to GAMS syntax
2. Use existing GAMS export features in some tools
3. Write the mathematical model directly in GAMS (it's very readable)

### Q8: How do I specify the output file?

**A:** Use the `-o` or `--output` flag:

```bash
nlp2mcp input.gms -o output.gms
```

If you omit `-o`, the MCP code is printed to stdout (useful for piping).

### Q9: Can I convert multiple files at once?

**A:** Not in a single command, but you can use a shell script:

```bash
for file in *.gms; do
  nlp2mcp "$file" -o "${file%.gms}_mcp.gms"
done
```

This converts all `.gms` files in the current directory.

### Q10: What does the `-v` flag do?

**A:** `-v` enables verbose output showing pipeline stages:

```bash
nlp2mcp model.gms -o output.gms -v
```

Output:
```
Parsing GAMS model...
Validating model structure...
Validating parameters...
Computing derivatives...
Assembling KKT system...
Generating MCP code...
Success!
```

Use `-vv` for very verbose output (includes detailed internal logs).

---

## Conversion Process

### Q11: What does nlp2mcp actually do?

**A:** nlp2mcp automatically derives the KKT (Karush-Kuhn-Tucker) optimality conditions for your NLP model and generates an equivalent MCP formulation.

**The process:**
1. Parse your GAMS NLP model
2. Compute symbolic derivatives (gradients and Jacobians)
3. Assemble KKT stationarity equations
4. Generate complementarity conditions for constraints and bounds
5. Emit GAMS MCP code with equation-variable pairings

### Q12: What is the KKT system?

**A:** The KKT conditions are first-order necessary conditions for optimality in constrained optimization.

**For a problem:**
```
minimize f(x)
subject to h(x) = 0  (equality constraints)
           g(x) ≤ 0  (inequality constraints)
           lo ≤ x ≤ up (bounds)
```

**KKT conditions:**
1. **Stationarity:** ∇f(x) + J_h^T·ν + J_g^T·λ - π^lo + π^up = 0
2. **Primal feasibility:** h(x) = 0, g(x) ≤ 0, lo ≤ x ≤ up
3. **Dual feasibility:** λ ≥ 0, π^lo ≥ 0, π^up ≥ 0
4. **Complementarity:** g(x)·λ = 0, (x-lo)·π^lo = 0, (up-x)·π^up = 0

nlp2mcp converts these conditions into an MCP that PATH can solve.

### Q13: What are multiplier variables?

**A:** Multipliers (also called dual variables or Lagrange multipliers) are variables that enforce constraints.

**In the MCP:**
- `nu_*`: Multipliers for equality constraints (free variables)
- `lam_*`: Multipliers for inequality constraints (≥ 0)
- `pi_lo_*`: Multipliers for lower bounds (≥ 0)
- `pi_up_*`: Multipliers for upper bounds (≥ 0)

**Economic interpretation:** Multipliers represent the "shadow price" or marginal value of relaxing a constraint.

### Q14: Why does the MCP have more variables than my original NLP?

**A:** The MCP includes all multiplier variables in addition to your original primal variables.

**Example:**
- Original NLP: 10 variables, 5 constraints, all bounded
- Generated MCP: 10 primal + 5 constraint multipliers + 20 bound multipliers = 35 variables

This is normal and expected. The MCP system size is roughly 3-4x the original NLP.

### Q15: Can nlp2mcp handle indexed variables and equations?

**A:** Yes, nlp2mcp fully supports GAMS indexed (subscripted) variables and equations.

```gams
Sets
    t  Time periods  /t1*t10/
    i  Products      /i1*i5/;

Variables
    production(i,t)  Production by product and time
    inventory(i,t)   Inventory levels
;

Equations
    balance(i,t)  Inventory balance equation
;

balance(i,t).. inventory(i,t) =E= inventory(i,t-1) + production(i,t) - demand(i,t);
```

nlp2mcp correctly handles the indexing in derivatives and generates indexed MCP equations.

---

## Advanced Features

### Q16: How does min/max reformulation work?

**A:** nlp2mcp automatically reformulates `min()` and `max()` using auxiliary variables and complementarity.

**For `z = max(x, y)`:**

Generated reformulation:
```gams
Variables
    z_aux      Auxiliary for max
    lam_x      Multiplier for x ≤ z_aux
    lam_y      Multiplier for y ≤ z_aux
;

Equations
    aux_ge_x   z_aux ≥ x
    aux_ge_y   z_aux ≥ y
;

aux_ge_x.. z_aux - x =G= 0;  * z_aux ≥ x
aux_ge_y.. z_aux - y =G= 0;  * z_aux ≥ y

* Complementarity ensures z_aux equals max(x,y):
* If x < y, then lam_x=0 (not binding), lam_y>0 (binding), z_aux=y
* If x > y, then lam_x>0 (binding), lam_y=0 (not binding), z_aux=x
```

**No special syntax needed** - just use `max()` or `min()` in your model.

### Q17: When should I use --smooth-abs?

**A:** Use `--smooth-abs` when your model contains `abs()` functions.

**Without flag:** Error - "abs() not supported"

**With flag:** Replaces `abs(x)` with smooth approximation `sqrt(x² + ε)`

**Accuracy:**
- Excellent for |x| ≥ 0.1 (< 0.1% error)
- Small error near x=0 (≤ ε)
- Default ε = 1e-6

**Trade-off:** Smooth approximation vs exact non-differentiable abs().

### Q18: What does --scale auto do?

**A:** `--scale auto` applies Curtis-Reid iterative scaling to improve numerical conditioning.

**When to use:**
- Variables/constraints have vastly different magnitudes (e.g., 1e-6 to 1e6)
- PATH reports numerical issues or poor convergence
- Model is ill-conditioned

**What it does:**
- Balances row and column norms in the KKT matrix
- Improves conditioning number
- Often helps PATH convergence

**Example:**
```bash
nlp2mcp model.gms -o output.gms --scale auto
```

### Q19: Can I use $include directives in my model?

**A:** Yes, nlp2mcp fully supports `$include`.

**Example:**
```gams
$include data.gms
$include equations.gms

Model mymodel /all/;
Solve mymodel using NLP minimizing obj;
```

nlp2mcp automatically:
- Resolves all includes (recursively)
- Handles relative paths (relative to the containing file)
- Detects circular includes (error if found)
- Processes the complete merged model

### Q20: What's the difference between --stats and -v?

**A:** Different types of output:

**`-v` (verbose):** Shows pipeline progress
```
Parsing GAMS model...
Computing derivatives...
Assembling KKT system...
```

**`--stats`:** Shows model statistics after conversion
```
Model Statistics:
  Equations: 50 (stationarity: 20, complementarity: 30)
  Variables: 50 (primal: 20, multipliers: 30)
  Jacobian nonzeros: 180
  Density: 7.2%
```

You can use both together: `nlp2mcp model.gms -o out.gms -v --stats`

---

## PATH Solver

### Q21: Do I need to configure PATH options for nlp2mcp-generated MCPs?

**A:** Usually no - default PATH options work well for most models.

**Default options are appropriate for:**
- Well-conditioned models
- Convex problems
- Models with smooth functions

**Consider custom options for:**
- Large models (increase iteration limits)
- Ill-conditioned models (adjust tolerance, enable proximal perturbation)
- Models failing to converge (try different crash methods)

See [PATH_SOLVER.md](PATH_SOLVER.md) for detailed guidance.

### Q22: What does Model Status 5 mean?

**A:** Model Status 5 = "Locally Infeasible"

**Possible causes:**
1. **Original NLP is infeasible** - Check if your NLP solves with CONOPT/IPOPT
2. **Non-convex problem** - KKT conditions are necessary but not sufficient for non-convex problems
3. **Numerical issues** - Try `--scale auto` or adjust PATH options
4. **Bad initial point** - Provide better starting values in GAMS

**Debugging steps:**
1. Verify original NLP solves: `gams original.gms`
2. Try scaling: `nlp2mcp model.gms -o out.gms --scale auto`
3. Check PATH solver output for specific errors
4. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics

### Q23: Can I use other MCP solvers besides PATH?

**A:** Yes, any GAMS MCP solver can solve the generated MCP.

**Available solvers:**
- **PATH** (recommended) - Robust, widely used, handles large models
- **MILES** - Alternative MCP solver
- **NLPEC** - For models with equilibrium constraints

**To use a different solver:**
```gams
option mcp = miles;  * Change from path to miles
solve model_mcp using MCP;
```

PATH is recommended for nlp2mcp-generated models due to its robustness.

### Q24: How do I interpret PATH iteration output?

**A:** PATH shows major iterations with merit function values and residuals.

**Example output:**
```
MAJOR ITERATION    0    FUNC-VALUE = 1.234e+02
MAJOR ITERATION    1    FUNC-VALUE = 5.678e+01
...
MAJOR ITERATION   10    FUNC-VALUE = 1.234e-08
```

**What to look for:**
- **Merit function decreasing:** Good, PATH is making progress
- **Rapid decrease:** Fast convergence, well-conditioned problem
- **Slow decrease:** May need more iterations or better options
- **Final value < 1e-6:** Converged (Model Status 1)

See [PATH_SOLVER.md](PATH_SOLVER.md) for interpreting Model Status codes.

### Q25: What are good PATH option settings for large models?

**A:** For models with 1000+ variables, use these settings:

Create `path.opt`:
```
convergence_tolerance 1e-6
major_iteration_limit 2000
crash_method pnewton
output_major_iterations 1
```

In your GAMS file:
```gams
model_mcp.optfile = 1;
option iterlim = 10000;
solve model_mcp using MCP;
```

Adjust based on convergence behavior. See [PATH_SOLVER.md](PATH_SOLVER.md) for more configurations.

---

## Troubleshooting

### Q26: Why does nlp2mcp say "Model has no objective function"?

**A:** Your GAMS file is missing a proper `Solve` statement.

**Correct:**
```gams
Model mymodel /all/;
Solve mymodel using NLP minimizing obj;  * Must specify minimizing/maximizing
```

**Incorrect:**
```gams
Solve mymodel;  * Missing objective specification
```

The `Solve` statement must include `minimizing <var>` or `maximizing <var>`.

### Q27: What does "Circular include detected" mean?

**A:** Your files include each other in a loop.

**Example of circular include:**
```
main.gms:
  $include data.gms

data.gms:
  $include main.gms  * CIRCULAR!
```

**Solution:** Restructure to avoid circular dependencies:
- Use a main file that includes sub-files
- Don't have sub-files include the main file
- Extract common code to a third file if needed

### Q28: Why am I getting NaN or Inf errors?

**A:** Invalid numerical values in your model data or expressions.

**Common causes:**

**1. Uninitialized parameters:**
```gams
Parameter p(i);
* p not initialized - may contain undefined values
```

**Solution:**
```gams
Parameter p(i);
p(i) = 0;  * Initialize
```

**2. Division by zero:**
```gams
obj =E= 1 / (x - 5);  * If x=5, division by zero
```

**Solution:** Add bounds or use conditional expressions.

**3. Invalid function inputs:**
```gams
obj =E= log(x);   * If x ≤ 0, log is undefined
obj =E= sqrt(x);  * If x < 0, sqrt is undefined
```

**Solution:**
```gams
x.lo = 0.001;  * Ensure x > 0
```

### Q29: The generated MCP is very large. Is this normal?

**A:** Yes, MCP files are typically 3-4x larger than the original NLP.

**Why:**
- Adds multiplier variables for all constraints and bounds
- Adds stationarity equations for all variables
- Adds complementarity equations
- Includes reformulation auxiliary variables (for min/max, etc.)

**File size comparison:**
- 100-variable NLP: ~500 lines → 1500-2000 lines MCP
- 1000-variable NLP: ~5000 lines → 15000-20000 lines MCP

**This is expected** - the MCP explicitly represents all optimality conditions.

### Q30: Can I modify the generated MCP by hand?

**A:** Yes, but be careful to maintain the MCP structure.

**Safe modifications:**
- Adjusting initial values (`.l` attributes)
- Adding bounds to multiplier variables
- Changing model/variable names

**Dangerous modifications:**
- Removing equations or variables (breaks pairing)
- Changing equation structure (may violate KKT conditions)
- Altering complementarity relationships

**Best practice:** Modify the original NLP and regenerate the MCP rather than hand-editing.

---

## Performance & Limitations

### Q31: How long should conversion take?

**A:** Typical performance benchmarks:

- **250 variables:** < 10 seconds
- **500 variables:** < 30 seconds
- **1000 variables:** < 90 seconds

**Factors affecting speed:**
- Number of variables and equations
- Expression complexity
- Sparsity of Jacobian
- Whether scaling is enabled

If conversion takes significantly longer, consider:
- Simplifying complex expressions
- Using `--quiet` to reduce I/O
- Checking for very dense Jacobian structures

### Q32: What is the largest model nlp2mcp can handle?

**A:** Successfully tested up to **1000 variables and 1000 equations**.

**Memory usage:**
- 500-variable model: ~60 MB
- 1000-variable model: ~150 MB (estimated)

**Practical limits:**
- Python memory limit (~few GB)
- Processing time (quadratic growth in Jacobian computation)

For larger models (10,000+ variables), consider:
- Model decomposition
- Exploiting special structure
- Using specialized NLP solvers directly

### Q33: Does nlp2mcp support all GAMS syntax?

**A:** nlp2mcp supports a comprehensive subset of GAMS syntax for NLP models.

**Fully supported:**
- Variables, Parameters, Scalars, Sets, Aliases
- Equations with =E=, =L=, =G= relations
- Bounds: .lo, .up, .fx
- Arithmetic operators: +, -, *, /, ^
- Functions: exp, log, sqrt, sin, cos, tan, min, max
- Aggregation: sum
- Indexed variables and equations
- $include directives
- Table data blocks
- Comments (*, //, $ontext...$offtext)

**Not supported:**
- Control flow: loop, if, while
- Dollar conditionals: $if, $set, $macro
- External functions
- Non-smooth functions without flags: abs (need --smooth-abs), sign, floor, ceil
- Dynamic sets or parameters

### Q34: Is nlp2mcp suitable for production use?

**A:** Yes, for appropriate use cases.

**nlp2mcp is production-ready for:**
- Converting well-formulated NLP models to MCP
- Analyzing KKT conditions
- Teaching optimization concepts
- Prototyping equilibrium models

**Current status: Beta (v0.5.0-beta)**
- API is stable
- Core functionality tested (972 passing tests)
- Used successfully on real-world models up to 1000 variables

**Before using in production:**
- Validate generated MCP against original NLP solution
- Test on representative models from your domain
- Have fallback to direct NLP solver if MCP approach fails

### Q35: How do I contribute to nlp2mcp?

**A:** Contributions are welcome!

**Ways to contribute:**
1. **Report bugs:** Open an issue on GitHub with minimal reproducing example
2. **Suggest features:** Open a discussion or feature request
3. **Improve documentation:** Submit pull requests for docs
4. **Add test cases:** Contribute example models
5. **Fix bugs:** Submit pull requests (see CONTRIBUTING.md)

**Before contributing code:**
- Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- Run tests: `pytest tests/`
- Check code style: `make lint`, `make typecheck`, `make format`
- Add tests for new features

GitHub: https://github.com/jeffreyhorn/nlp2mcp

---

## Additional Resources

- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md) - Complete reference
- **Tutorial:** [TUTORIAL.md](TUTORIAL.md) - Step-by-step learning
- **PATH Solver Guide:** [PATH_SOLVER.md](PATH_SOLVER.md) - Solver configuration
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem diagnosis
- **API Documentation:** [API docs](api/index.html) - Developer reference

---

**Can't find your question?** 

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for problem-specific guidance
- Open a discussion on GitHub: https://github.com/jeffreyhorn/nlp2mcp/discussions
- Report a bug: https://github.com/jeffreyhorn/nlp2mcp/issues

**Last updated:** November 8, 2025
