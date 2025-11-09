# nlp2mcp Troubleshooting Guide

**Diagnose and fix common issues with nlp2mcp**

Version: 0.5.0-beta  
Last Updated: 2025-11-08

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Parsing Errors](#parsing-errors)
3. [Model Validation Errors](#model-validation-errors)
4. [Conversion Failures](#conversion-failures)
5. [Numerical Errors](#numerical-errors)
6. [PATH Solver Issues](#path-solver-issues)
7. [Performance Problems](#performance-problems)
8. [Output Issues](#output-issues)

---

## How to Use This Guide

Each issue follows a **Problem → Diagnosis → Solution** format:

1. **Problem:** Error message or symptom
2. **Diagnosis:** How to identify the root cause
3. **Solution:** Step-by-step fix

---

## Installation Issues

### Issue 1.1: "Python version not supported"

**Problem:**
```
ERROR: Package 'nlp2mcp' requires a different Python: 3.10.0 not in '>=3.11'
```

**Diagnosis:**
Your Python version is too old. Check version:
```bash
python --version
```

**Solution:**

**Option A: Upgrade Python (recommended)**
```bash
# macOS (via Homebrew)
brew install python@3.12

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12

# Windows
# Download from python.org
```

**Option B: Use pyenv for version management**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# Install nlp2mcp
pip install nlp2mcp
```

---

### Issue 1.2: "No module named 'lark'"

**Problem:**
```
ModuleNotFoundError: No module named 'lark'
```

**Diagnosis:**
Dependencies not installed. This happens if you cloned the repo without installing.

**Solution:**
```bash
# If using pip install:
pip install nlp2mcp

# If installing from source:
cd nlp2mcp
pip install -e .

# Verify installation:
python -c "import lark; print(lark.__version__)"
```

---

### Issue 1.3: "command not found: nlp2mcp"

**Problem:**
```bash
$ nlp2mcp --help
zsh: command not found: nlp2mcp
```

**Diagnosis:**
CLI entry point not in PATH. Check where pip installed it:
```bash
pip show nlp2mcp | grep Location
```

**Solution:**

**Option A: Ensure Python scripts directory is in PATH**
```bash
# Find scripts directory
python -m site --user-base

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$HOME/.local/bin"

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

**Option B: Use python -m**
```bash
python -m src.cli --help
```

**Option C: Reinstall with --user flag**
```bash
pip install --user nlp2mcp
```

---

## Parsing Errors

### Issue 2.1: "Unexpected token"

**Problem:**
```
ParseError: Unexpected token 'IF' at line 42, column 5
```

**Diagnosis:**
You're using GAMS control flow syntax, which nlp2mcp doesn't support.

**Unsupported:** `$if`, `$set`, `loop`, `if`, `while`

**Solution:**

**For conditional compilation ($if):**
```gams
* Unsupported:
$if %debug% == 1 $include debug.gms

* Solution: Pre-process or remove conditionals
```

**For loops:**
```gams
* Unsupported:
loop(t,
  production(t) = production(t-1) + increment;
);

* Solution: Use GAMS built-in sum/product or rewrite as equations
Equations prod_balance(t);
prod_balance(t).. production(t) =E= production(t-1) + increment;
```

**Workaround:** Remove unsupported constructs or use a GAMS pre-processor.

---

### Issue 2.2: "File not found"

**Problem:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'model.gms'
```

**Diagnosis:**
Input file doesn't exist or path is wrong.

**Solution:**

**Check file exists:**
```bash
ls -l model.gms
```

**Use absolute path:**
```bash
nlp2mcp /full/path/to/model.gms -o output.gms
```

**Check current directory:**
```bash
pwd
ls *.gms
```

---

### Issue 2.3: "$include file not found"

**Problem:**
```
IncludeError: Could not find included file 'data.gms' referenced from 'main.gms'
```

**Diagnosis:**
The `$include` directive references a file that doesn't exist.

**Solution:**

**Check relative path:**
```gams
* If main.gms is in /project/
* And data.gms is in /project/data/

* Correct:
$include data/data.gms

* Incorrect:
$include data.gms  * File not in same directory
```

**Verify file exists:**
```bash
ls -R *.gms
```

**Use absolute path (not recommended):**
```gams
$include /full/path/to/data.gms
```

---

### Issue 2.4: "Circular include detected"

**Problem:**
```
CircularIncludeError: Circular include chain detected: main.gms -> data.gms -> main.gms
```

**Diagnosis:**
Files include each other in a loop.

**Solution:**

**Identify the cycle:**
```
main.gms includes data.gms
data.gms includes main.gms  ← CIRCULAR!
```

**Fix by restructuring:**
```gams
* main.gms
$include data.gms
$include equations.gms
Model mymodel /all/;

* data.gms
* (no includes, just data)

* equations.gms
* (no includes, just equations)
```

**Rule:** Never have included files include the parent file.

---

## Model Validation Errors

### Issue 3.1: "Model has no objective function defined"

**Problem:**
```
ModelError: Model has no objective function defined

Suggestion:
Add an objective definition to your GAMS model
```

**Diagnosis:**
Missing or incorrect `Solve` statement.

**Solution:**

**Correct format:**
```gams
Variables x, y, obj;

Equations
    objective  Define objective
;

objective.. obj =E= sqr(x - 2) + sqr(y - 3);

Model mymodel /all/;
Solve mymodel using NLP minimizing obj;  * Must have minimizing/maximizing
```

**Common mistakes:**
```gams
* Mistake 1: No Solve statement
Model mymodel /all/;
* → Add: Solve mymodel using NLP minimizing obj;

* Mistake 2: Solve without objective
Solve mymodel;
* → Fix: Solve mymodel using NLP minimizing obj;

* Mistake 3: Objective variable not defined
Solve mymodel using NLP minimizing cost;  * 'cost' not declared
* → Fix: Declare 'cost' in Variables section
```

---

### Issue 3.2: "Equation references no variables"

**Problem:**
```
ModelError: Equation 'const_eq' references no variables (constant equation)

Suggestion:
This equation is always true or always false.
```

**Diagnosis:**
Equation has no variables, only constants or parameters.

**Solution:**

**Identify the problem equation:**
```gams
* Bad:
const_eq.. 5 =E= 5;  * Always true, no variables

* Bad:
param_eq.. p1 =E= p2;  * Only parameters, no variables
```

**Fix options:**

**Option 1: Remove the equation** (if it's redundant)
```gams
* Just remove const_eq
```

**Option 2: Add variables**
```gams
* Intended: Set x to 5
fix_x.. x =E= 5;  * Now x is a variable
```

**Option 3: Use parameter assignment**
```gams
* If setting parameter values, use assignment not equation:
p1 = p2;  * Parameter assignment, not equation
```

---

### Issue 3.3: "Circular variable definition detected"

**Problem:**
```
ModelError: Circular variable definition detected: x -> y -> x

Suggestion:
Variables cannot have circular definitions.
```

**Diagnosis:**
Variables define each other in a loop.

**Solution:**

**Identify the cycle:**
```gams
* Bad:
eq1.. x =E= y;
eq2.. y =E= x;  * x depends on y, y depends on x → CIRCULAR!
```

**Fix by breaking the cycle:**
```gams
* Option 1: One variable is exogenous (parameter)
Parameter y;
y = 5;
eq1.. x =E= y;  * Now x = 5, no circularity

* Option 2: Add another equation/variable
eq1.. x =E= y + z;
eq2.. y =E= x - z;
eq3.. z =E= 10;  * z breaks the cycle
```

**Note:** Self-references are OK:
```gams
* OK: Variable references itself
eq.. x =E= x + 1;  * Mathematically valid (though unusual)
```

---

### Issue 3.4: "Variable never used"

**Problem:**
```
WARNING: Variable 'unused_var' declared but never referenced in equations
```

**Diagnosis:**
Variable declared but not appearing in any equation.

**Solution:**

**Check for typos:**
```gams
Variables production, inventory;

Equations balance;
balance.. inventry =E= production + ...;  * Typo: 'inventry' not 'inventory'
```

**Remove unused variables:**
```gams
* If variable truly not needed:
Variables x, y;  * Remove unused_var
```

**This is a WARNING, not an error** - conversion will still proceed.

---

## Conversion Failures

### Issue 4.1: "abs() not supported without --smooth-abs"

**Problem:**
```
UnsupportedFunctionError: Function 'abs' not supported without --smooth-abs flag
```

**Diagnosis:**
Model uses `abs()`, which is non-differentiable.

**Solution:**

**Use smooth approximation:**
```bash
nlp2mcp model.gms -o output.gms --smooth-abs
```

**What this does:**
```gams
* Original:
obj =E= abs(x - 5);

* Converted to:
obj =E= sqrt(power(x - 5, 2) + 1e-6);
```

**Adjust epsilon if needed:**
```bash
nlp2mcp model.gms -o output.gms --smooth-abs --smooth-abs-epsilon 1e-8
```

**Accuracy:**
- Excellent for |x| ≥ 0.1
- Small error near x=0 (≤ ε)

**Alternative:** Reformulate your model to avoid abs() if possible.

---

### Issue 4.2: "Unsupported function"

**Problem:**
```
UnsupportedFunctionError: Function 'sign' is not supported
```

**Diagnosis:**
Model uses a function that nlp2mcp cannot handle.

**Unsupported functions:**
- `sign(x)` - discontinuous
- `floor(x)`, `ceil(x)` - discrete
- `mod(x,y)` - non-smooth
- External functions

**Solution:**

**Option 1: Reformulate the model**
```gams
* Instead of: sign(x) = {-1 if x<0, 0 if x=0, +1 if x>0}
* Use binary variable or complementarity

Variables x, y;
Binary variable b;
Equations
    eq1, eq2;
;

eq1.. y =L= M * b;      * If b=0, y≤0
eq2.. y =G= -M * (1-b); * If b=1, y≥0
```

**Option 2: Smooth approximation**
```gams
* sign(x) ≈ tanh(k*x)  where k is large
* sign(x) ≈ 2/(1 + exp(-k*x)) - 1
```

**Option 3: Use different solver/approach**
- Consider solving as MINLP (for binary variables)
- Use complementarity formulation
- Solve original NLP directly

---

### Issue 4.3: "Expression too complex"

**Problem:**
```
Error: Maximum recursion depth exceeded during derivative computation
```

**Diagnosis:**
Expression is deeply nested or very large.

**Solution:**

**Simplify expressions:**
```gams
* Bad: Deeply nested
obj =E= exp(log(sqrt(sin(cos(tan(x))))));

* Good: Intermediate variables
Variables t1, t2, t3;
Equations calc1, calc2, calc3;
calc1.. t1 =E= tan(x);
calc2.. t2 =E= cos(t1);
calc3.. obj =E= exp(log(sqrt(sin(t2))));
```

**Break up large sums:**
```gams
* Bad: Single huge equation
obj =E= sum((i,j,k,l,m), x(i)*y(j)*z(k)*w(l)*v(m)*...);

* Good: Intermediate aggregations
Variables partial1(i,j), partial2(i,j,k);
Equations agg1, agg2;
agg1(i,j).. partial1(i,j) =E= sum(k, x(i)*y(j)*z(k));
agg2(i,j,k).. partial2(i,j,k) =E= partial1(i,j) * w(k);
...
```

---

## Numerical Errors

### Issue 5.1: "NaN value detected"

**Problem:**
```
NumericalError: Parameter 'p[1]' has invalid value (value is NaN)

Suggestion:
Check your GAMS model for uninitialized parameters
```

**Diagnosis:**
Parameter contains NaN (Not a Number).

**Solution:**

**Initialize all parameters:**
```gams
* Bad:
Parameter demand(t);
* demand not initialized → may be NaN

* Good:
Parameter demand(t);
demand(t) = 0;  * Initialize before use
demand('t1') = 100;
demand('t2') = 120;
```

**Check Table definitions:**
```gams
Table data(i,j)
       j1   j2   j3
  i1   10   20   30
  i2   40   50     ;  * Missing j3 for i2 → will be 0 (OK)
```

**Missing values in Tables become 0, not NaN** (GAMS behavior).

**Check for division by zero:**
```gams
* Bad:
p1 = p2 / 0;  * Results in Inf or error

* Good:
p1 = p2 / (p3 + 1e-10);  * Avoid exact zero
```

---

### Issue 5.2: "Inf value detected"

**Problem:**
```
NumericalError: Computed value is infinite (value is +Inf)
```

**Diagnosis:**
Expression evaluates to infinity.

**Solution:**

**Common causes:**

**1. Division by zero:**
```gams
* Bad:
obj =E= 1 / (x - 5);  * If x=5, division by zero

* Good: Add bounds
x.lo = 0;
x.up = 4.99;  * Ensure x ≠ 5

* Or: Reformulate
obj =E= x - 5;  * Different model avoiding division
```

**2. Overflow:**
```gams
* Bad:
obj =E= exp(1000 * x);  * If x large, exp overflows

* Good: Bound variables
x.up = 10;  * Ensure exp(1000*x) computable

* Or: Rescale
obj =E= exp(x);  * Don't multiply by 1000
```

**3. log(0):**
```gams
* Bad:
obj =E= log(x);  * If x=0, log(0) = -Inf

* Good: Bound away from zero
x.lo = 1e-6;
```

---

### Issue 5.3: "Invalid bound: lower > upper"

**Problem:**
```
NumericalError: Variable 'x' has inconsistent bounds: lo=10 > up=5
```

**Diagnosis:**
Variable's lower bound exceeds upper bound.

**Solution:**

**Fix the bounds:**
```gams
* Bad:
x.lo = 10;
x.up = 5;  * Inconsistent!

* Good:
x.lo = 5;
x.up = 10;
```

**Check for parameter errors:**
```gams
* If using parameters:
Parameters lo_bound, up_bound;
lo_bound = 10;
up_bound = 5;  * Mistake in values

x.lo = lo_bound;
x.up = up_bound;  * Results in invalid bounds

* Fix: Swap values
lo_bound = 5;
up_bound = 10;
```

---

## PATH Solver Issues

### Issue 6.1: "Model Status 5: Locally Infeasible"

**Problem:**
```
*** Model Status: 5 (Locally Infeasible)
```

**Diagnosis:**
PATH couldn't find a solution satisfying all constraints.

**Possible causes:**
1. Original NLP is infeasible
2. Model is non-convex (KKT necessary but not sufficient)
3. Poor numerical conditioning
4. Bad initial point

**Solution:**

**Step 1: Verify original NLP solves**
```bash
# Solve original NLP with CONOPT
gams original.gms

# Check model status
# If original fails → NLP is infeasible, fix constraints
```

**Step 2: Try scaling**
```bash
nlp2mcp model.gms -o output.gms --scale auto
gams output.gms
```

**Step 3: Adjust PATH options**

Create `path.opt`:
```
convergence_tolerance 1e-4
major_iteration_limit 2000
crash_method none
proximal_perturbation 1e-3
```

In GAMS:
```gams
model_mcp.optfile = 1;
solve model_mcp using MCP;
```

**Step 4: Provide better initial point**
```gams
* Set starting values closer to expected solution
x.l = 5;
y.l = 3;
```

**Step 5: Check for non-convexity**

If model is non-convex, KKT conditions may have multiple local solutions or no solution. Consider:
- Solving original NLP directly
- Using global optimization solver
- Reformulating to convex problem

---

### Issue 6.2: "Model Status 4: Infeasible"

**Problem:**
```
*** Model Status: 4 (Infeasible)
```

**Diagnosis:**
PATH determined the problem is infeasible (no solution exists).

**Solution:**

**Check constraints:**
```gams
* Conflicting constraints:
eq1.. x + y =E= 10;
eq2.. x + y =E= 20;  * Impossible!

* Infeasible bounds:
x.lo = 5;
eq1.. x =L= 3;  * x ≥ 5 and x ≤ 3 → infeasible
```

**Relax constraints:**
```gams
* Change equality to inequality if appropriate:
eq1.. x + y =L= 10;  * Instead of =E=

* Widen bounds:
x.lo = 0;  * Instead of x.lo = 5
```

**Check parameter values:**
```gams
* Ensure parameters make sense:
Parameter demand, capacity;
demand = 100;
capacity = 50;
balance.. production =L= capacity;
satisfy.. production =G= demand;  * Infeasible if demand > capacity
```

---

### Issue 6.3: "Model Status 2: Iteration Limit"

**Problem:**
```
*** Model Status: 2 (Locally Optimal - Iteration Limit Interrupted)
```

**Diagnosis:**
PATH hit iteration limit before fully converging.

**Solution:**

**Increase iteration limits:**

In GAMS:
```gams
option iterlim = 10000;  * Default: 2000
model_mcp.optfile = 1;
solve model_mcp using MCP;
```

In `path.opt`:
```
major_iteration_limit 5000
```

**Check convergence:**
```
Final function value: 1.234e-05
```

If function value is small (< 1e-4), solution is probably good enough despite iteration limit.

**Improve convergence speed:**
- Try `--scale auto`
- Provide better initial point
- Simplify model if possible

---

### Issue 6.4: "PATH crashes or hangs"

**Problem:**
PATH stops responding or crashes without error message.

**Diagnosis:**
Numerical issues or memory problems.

**Solution:**

**Step 1: Enable PATH output**
```gams
option sysout = on;  * Show PATH output
model_mcp.optfile = 1;
solve model_mcp using MCP;
```

**Step 2: Try different crash method**

In `path.opt`:
```
crash_method none
output_crash_iterations 1
output_major_iterations 1
```

**Step 3: Check for numerical issues**
```bash
nlp2mcp model.gms -o output.gms --stats
# Check Jacobian density and condition
```

**Step 4: Reduce model size**
- Test with smaller subset of data
- Fix some variables to reduce problem size
- Identify problematic equations

**Step 5: Use proximal perturbation**

In `path.opt`:
```
proximal_perturbation 1e-2
```

This adds regularization to handle singular matrices.

---

## Performance Problems

### Issue 7.1: "Conversion is very slow"

**Problem:**
Conversion takes much longer than expected.

**Diagnosis:**
Large model or complex expressions.

**Solution:**

**Check model size:**
```bash
nlp2mcp model.gms -o output.gms --stats
```

Expected times:
- 250 vars: < 10s
- 500 vars: < 30s
- 1000 vars: < 90s

**If slower than expected:**

**Use quiet mode:**
```bash
nlp2mcp model.gms -o output.gms --quiet
# Reduces I/O overhead
```

**Simplify expressions:**
```gams
* Break up complex nested expressions
* Use intermediate variables
```

**Check Jacobian density:**
```bash
nlp2mcp model.gms --dump-jacobian jac.mtx --stats
# High density (>50%) slows computation
```

---

### Issue 7.2: "Out of memory"

**Problem:**
```
MemoryError: Unable to allocate array
```

**Diagnosis:**
Model too large for available memory.

**Solution:**

**Check memory usage:**
```bash
# Run with monitoring
/usr/bin/time -v nlp2mcp model.gms -o output.gms
# Look for "Maximum resident set size"
```

**Reduce memory usage:**

**1. Process in smaller chunks:**
Break model into sub-models if possible.

**2. Reduce model size:**
```gams
* Fix some variables
x.fx = 5;  * Fixed variables don't add multipliers

* Aggregate indexed variables
* Use fewer time periods or products
```

**3. Use sparse structures:**
nlp2mcp uses sparse Jacobians by default, but very dense models still require significant memory.

**4. Increase system memory:**
- Close other applications
- Use machine with more RAM
- Use cloud VM with larger memory

---

## Output Issues

### Issue 8.1: "Generated MCP has syntax errors"

**Problem:**
```
gams output_mcp.gms
*** Syntax Error at line 42
```

**Diagnosis:**
Generated GAMS code has syntax errors (this is a bug).

**Solution:**

**Step 1: Report the bug**
This shouldn't happen - please report:
- GitHub: https://github.com/jeffreyhorn/nlp2mcp/issues
- Include minimal reproducing example
- Include nlp2mcp version: `nlp2mcp --version`

**Step 2: Workaround**

**Check for naming conflicts:**
```gams
* If your model uses reserved names:
Variables stat_x;  * Conflicts with generated name
```

nlp2mcp generates names like `stat_x`, `pi_lo_x`, `nu_*`, `lam_*`. Avoid these in your model.

**Step 3: Manual fix (temporary)**
Open `output_mcp.gms` and fix the syntax error, but report the bug so it can be fixed in nlp2mcp.

---

### Issue 8.2: "MCP has different solution than NLP"

**Problem:**
MCP and NLP converge to different solutions.

**Diagnosis:**
Non-convex problem with multiple local optima.

**Solution:**

**Step 1: Verify both are locally optimal**
```bash
# Solve NLP
gams original.gms
# Note: obj* = 123.45, Model Status 2

# Solve MCP
gams output_mcp.gms
# Note: obj* = 678.90, Model Status 1
```

**Step 2: Check objective values**
If MCP objective is worse than NLP:
- MCP found different local optimum
- MCP may have convergence issues

If MCP objective is better than NLP:
- NLP stopped at local minimum
- MCP found global minimum (rare)

**Step 3: Try different initial points**
```gams
* In MCP, set initial values closer to NLP solution
x.l = <NLP solution value>;
```

**Step 4: Accept non-uniqueness**
For non-convex problems, multiple local optima are expected. KKT conditions are necessary but not sufficient.

**Recommendation:** For non-convex problems, solve NLP directly with global optimization solver.

---

### Issue 8.3: "Output file is empty or truncated"

**Problem:**
Generated MCP file is empty or incomplete.

**Diagnosis:**
Write error or crash during generation.

**Solution:**

**Check disk space:**
```bash
df -h .
```

**Check permissions:**
```bash
ls -l output_mcp.gms
# Ensure you have write permission
```

**Try stdout first:**
```bash
nlp2mcp model.gms > output_mcp.gms
# Redirect stdout to file
```

**Check for crashes:**
```bash
nlp2mcp model.gms -o output_mcp.gms -vv
# Very verbose - shows where crash occurs
```

---

## Getting More Help

### When to Report a Bug

Report bugs if you encounter:
- Crashes or Python exceptions
- Generated GAMS code with syntax errors
- Incorrect KKT conditions (verify mathematically first)
- Memory leaks or excessive memory usage
- Parsing errors for valid GAMS syntax

### How to Report a Bug

1. **Check existing issues:** https://github.com/jeffreyhorn/nlp2mcp/issues
2. **Create minimal reproducing example:**
   ```gams
   * Smallest model that triggers the bug
   ```
3. **Include version info:**
   ```bash
   nlp2mcp --version
   python --version
   pip show nlp2mcp
   ```
4. **Provide full error message**
5. **Describe expected vs actual behavior**

### Additional Resources

- **FAQ:** [FAQ.md](FAQ.md) - Common questions
- **Tutorial:** [TUTORIAL.md](TUTORIAL.md) - Learning guide
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md) - Complete reference
- **PATH Guide:** [PATH_SOLVER.md](PATH_SOLVER.md) - Solver options
- **API Docs:** [API documentation](api/index.html) - Developer reference

### Community Support

- **Discussions:** https://github.com/jeffreyhorn/nlp2mcp/discussions
- **Issues:** https://github.com/jeffreyhorn/nlp2mcp/issues
- **Email:** jeffreydhorn@gmail.com (for private inquiries)

---

**Last updated:** November 8, 2025

**Can't find your issue?** Search the FAQ or open a discussion on GitHub.
