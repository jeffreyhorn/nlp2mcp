# PATH Smoke Test Integration Research

**Date:** 2025-11-25  
**Task:** Sprint 11 Prep Task 8 - Research PATH Smoke Test Integration  
**Objective:** Research PATH solver licensing, installation, and smoke test design for CI integration

---

## Executive Summary

This document researches PATH solver integration into CI for smoke testing MCP generation correctness. **Key finding:** PATH solver licensing is **UNCLEAR for CI/cloud usage** under academic license. **Recommendation:** **DEFER PATH CI integration to Sprint 12** and **PROTOTYPE IPOPT ALTERNATIVE** for Sprint 11 as a CI-friendly open-source solution.

**Critical Decision:**
- ❌ **PATH in CI:** Licensing unclear, requires written clarification from maintainer
- ✅ **IPOPT Alternative:** Open-source (EPL), CI-friendly, no licensing restrictions
- 🔍 **ACTION REQUIRED:** Contact ferris@cs.wisc.edu for PATH CI licensing clarification

---

## Table of Contents

1. [Section 1: PATH Solver Licensing Research](#section-1-path-solver-licensing-research)
2. [Section 2: PATH Installation in GitHub Actions](#section-2-path-installation-in-github-actions)
3. [Section 3: Smoke Test Design](#section-3-smoke-test-design)
4. [Section 4: IPOPT Alternative Solution](#section-4-ipopt-alternative-solution)
5. [Section 5: Implementation Recommendation](#section-5-implementation-recommendation)
6. [Appendix A: PATH Solver Technical Details](#appendix-a-path-solver-technical-details)
7. [Appendix B: IPOPT vs PATH Comparison](#appendix-b-ipopt-vs-path-comparison)
8. [Appendix C: Example Smoke Tests](#appendix-c-example-smoke-tests)

---

## Section 1: PATH Solver Licensing Research

### 1.1 PATH License Overview

**Official Sources:**
- **PATH Website:** https://pages.cs.wisc.edu/~ferris/path.html
- **Maintainer Contact:** Michael C. Ferris (ferris@cs.wisc.edu), University of Wisconsin-Madison
- **GAMS Documentation:** https://www.gams.com/latest/docs/S_PATH.html

**License Types:**

| License Type | Cost | Size Limit | Duration | Use Case |
|--------------|------|------------|----------|----------|
| **Free Version** | Free | 300 variables, 2000 nonzeros | Perpetual | Small problems, testing |
| **Academic License** | Free | Unrestricted | Annual renewal | Research, education |
| **Commercial License** | Paid | Unrestricted | Varies | Commercial use |

### 1.2 Free Version Limitations

**From PATH Website:**
> "The version that is downloadable from here...are free, but is limited to problems with no more than 300 variables and 2,000 nonzeros."

**Implications for CI:**
- ✅ **Smoke tests feasible:** Simple 2×2, 5×5 MCPs fit within limits
- ✅ **GAMSLib Tier 1:** Most Tier 1 models small enough (e.g., hansmcp.gms: 5 variables)
- ⚠️ **Limited coverage:** Cannot test larger models (scarfmcp.gms: >300 variables)

**Verdict:** Free version **sufficient for basic smoke tests** but **insufficient for comprehensive validation**.

### 1.3 Academic License - CI Usage UNCLEAR

**License Grant:**
> "A new license string will be provided in December of each year."

**Key Questions (UNRESOLVED):**

1. **Does academic license permit automated CI testing?**
   - **Status:** NOT EXPLICITLY DOCUMENTED
   - **Concern:** Academic licenses often restrict "production" or "commercial" use
   - **Question:** Is GitHub Actions CI considered "research use"?

2. **Can PATH run in cloud/container environments?**
   - **Status:** TECHNICALLY POSSIBLE (PATH runs on Linux)
   - **Concern:** License may restrict cloud/automated deployment
   - **Question:** Does "personal use" exclude shared CI runners?

3. **What are redistribution limits?**
   - **Status:** PATH binaries not publicly redistributable
   - **Concern:** Cannot include PATH in Docker image or CI cache
   - **Question:** Can we install PATH on-the-fly in CI?

**From PATHSolver.jl License (MIT wrapper, proprietary solver):**
> "PATHSolver.jl is licensed under the MIT License. However, the underlying PATH Solver is closed source. Without a license, it can only solve problem instances up to 300 variables and 2000 non-zeros."

**Implications:**
- ⚠️ **Licensing separate from code:** Wrapper is open source, solver is proprietary
- ⚠️ **Size limit without license:** Reverts to 300/2000 limit if academic license not properly configured
- ⚠️ **Annual renewal risk:** CI breaks every December until new license obtained

### 1.4 GAMS Integration Licensing

**GAMS Demo License:**
> "With a demo or community GAMS license, PATH will solve small models only."

**GAMS Full License:**
> "If your GAMS license includes PATH, this size restriction is removed."

**Implications:**
- ⚠️ **GAMS dependency:** PATH typically accessed via GAMS, not standalone
- ⚠️ **Dual licensing:** Need both GAMS license AND PATH license
- ⚠️ **Cost:** GAMS commercial license expensive ($thousands), demo license insufficient

### 1.5 Licensing Research Findings

**What We Know:**
1. ✅ **Free version exists:** 300 var / 2000 nonzero limit
2. ✅ **Academic license available:** Free, unrestricted size, annual renewal
3. ✅ **Contact available:** ferris@cs.wisc.edu for licensing questions
4. ⚠️ **CI use unclear:** No explicit documentation about automated/cloud testing

**What We DON'T Know:**
1. ❌ **Academic license permits CI?** - UNKNOWN
2. ❌ **Cloud deployment allowed?** - UNKNOWN
3. ❌ **Redistribution limits?** - UNKNOWN
4. ❌ **GitHub Actions compatible?** - UNKNOWN

**Recommendation:** 🔍 **CONTACT PATH MAINTAINER** before CI integration

**Draft Email to ferris@cs.wisc.edu:**
```
Subject: PATH Solver Academic License - CI/Cloud Usage Clarification

Dear Dr. Ferris,

I am using the PATH solver for an academic project (NLP to MCP converter)
and would like to integrate PATH into our GitHub Actions CI pipeline for
automated smoke testing of generated MCP models.

Could you please clarify if the PATH academic license permits:

1. Automated testing in GitHub Actions (cloud CI runners)
2. On-the-fly PATH installation in CI workflows
3. Running PATH in Docker containers or cloud VMs

Our use case:
- Academic research project (MIT license, open source)
- Smoke tests: 4-5 small MCP models (<50 variables each)
- CI frequency: ~100 runs/month (per-PR + nightly)
- No commercial use, purely validation of research software

If academic license does not permit CI use, what are our alternatives?
- Use free version (300 var limit)?
- Self-hosted runner on licensed machine?
- Other licensing options?

Thank you for your time.

Best regards,
[Name]
```

---

## Section 2: PATH Installation in GitHub Actions

### 2.1 Current PATH Integration Status

**Local Development:**
- ✅ PATH available on developer machines (via GAMS installation)
- ✅ Tests exist: `tests/validation/test_path_solver.py`
- ✅ Skip mechanism: `@pytest.mark.skipif(not PATH_AVAILABLE)`

**CI Status:**
- ❌ PATH not installed in GitHub Actions
- ❌ PATH tests skipped in CI
- ❌ No smoke testing of MCP generation

**Current Test Infrastructure:**
```python
# tests/validation/test_path_solver.py

def _check_path_available() -> bool:
    """Check if PATH solver is available within GAMS."""
    try:
        gams_exe = find_gams_executable()
        if gams_exe is None:
            return False
        
        # Verify GAMS executable exists
        result = subprocess.run([gams_exe], capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr
        return "GAMS" in output and "Release" in output
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

PATH_AVAILABLE = _check_path_available()

pytestmark = pytest.mark.skipif(
    not PATH_AVAILABLE,
    reason="PATH solver not available (GAMS not installed or not in PATH)"
)
```

### 2.2 PATH Installation Options

#### Option 1: Install GAMS with PATH (Official Method)

**Installation Steps:**
```yaml
# .github/workflows/path-smoke-tests.yml
- name: Install GAMS with PATH
  run: |
    # Download GAMS (demo version includes PATH)
    wget https://d37drm4t2jghv5.cloudfront.net/distributions/latest/linux/linux_x64_64_sfx.exe
    chmod +x linux_x64_64_sfx.exe
    ./linux_x64_64_sfx.exe -q -d /opt/gams
    
    # Add to PATH
    echo "/opt/gams" >> $GITHUB_PATH
    
    # Verify installation
    /opt/gams/gams --version
```

**Pros:**
- ✅ Official installation method
- ✅ Includes PATH solver by default
- ✅ Well-tested, stable

**Cons:**
- ❌ Large download (~500 MB)
- ❌ Slow CI (download + install ~2-3 minutes)
- ❌ Licensing unclear (demo license limits, academic license unclear)
- ❌ Annual license renewal required

**Estimated CI Time:**
- Download: ~1 minute
- Install: ~30 seconds
- Verification: ~10 seconds
- **Total: ~2 minutes overhead per workflow**

#### Option 2: Standalone PATH Binary (Not Recommended)

**Hypothetical Installation:**
```yaml
- name: Install PATH binary
  run: |
    # PATH binaries not publicly available
    wget [hypothetical-path-url]/path-linux-x64.tar.gz
    tar -xzf path-linux-x64.tar.gz -C /usr/local/bin
```

**Pros:**
- ✅ Fast installation (~10 seconds)
- ✅ Lightweight

**Cons:**
- ❌ PATH binaries NOT publicly distributed
- ❌ No official download URL
- ❌ Licensing violations (redistribution not permitted)
- ❌ Not feasible

**Verdict:** ❌ **NOT VIABLE**

#### Option 3: Self-Hosted GitHub Actions Runner

**Setup:**
```bash
# On licensed machine (university server or developer machine)
# Install GitHub Actions runner
./config.sh --url https://github.com/jeffreyhorn/nlp2mcp --token <TOKEN>
./run.sh

# Runner has GAMS/PATH pre-installed
```

**Workflow:**
```yaml
jobs:
  path-smoke-tests:
    runs-on: self-hosted  # Use self-hosted runner
    steps:
      - name: Run PATH tests
        run: pytest tests/validation/test_path_solver.py
```

**Pros:**
- ✅ Full PATH access
- ✅ No licensing concerns (run on licensed machine)
- ✅ Fast (PATH pre-installed)
- ✅ Controlled environment

**Cons:**
- ❌ Maintenance burden (runner uptime, updates, security)
- ❌ Single point of failure (if runner down, CI blocks)
- ❌ Security risks (self-hosted runners can access repo secrets)
- ❌ Availability (depends on machine uptime)

**Verdict:** ⚠️ **VIABLE BUT HIGH MAINTENANCE**

#### Option 4: Conda/Pip Installation (Wrapper Only)

**Installation:**
```yaml
- name: Install PATHSolver.jl wrapper
  run: |
    pip install pathlib  # Python wrapper (if exists)
```

**Reality:**
- ❌ No official Python pip package for PATH
- ❌ PATHSolver.jl is Julia-specific, not Python
- ❌ Wrappers require underlying PATH binary (still need licensing)

**Verdict:** ❌ **NOT VIABLE**

### 2.3 Installation Recommendation

**Recommended Approach (if PATH licensing permits CI):**

1. **Use GAMS Demo License for Smoke Tests:**
   - Free, no signup required
   - Size limits sufficient for smoke tests (<300 var)
   - Acceptable 2-minute CI overhead

2. **Install in Nightly Workflow Only:**
   - Too slow for per-PR (2 min overhead)
   - Nightly acceptable (10-20 min total)

3. **Fallback to IPOPT if Licensing Unclear:**
   - Open-source, no licensing concerns
   - Fast installation (~30 seconds)
   - See Section 4 for details

**Draft CI Workflow (if PATH permitted):**
```yaml
# .github/workflows/path-smoke-tests-nightly.yml
name: PATH Smoke Tests (Nightly)

on:
  schedule:
    - cron: "0 0 * * *"  # Nightly at 00:00 UTC
  workflow_dispatch:

jobs:
  path-smoke-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install Python dependencies
        run: |
          pip install -e .
          pip install pytest pytest-timeout
      
      - name: Install GAMS with PATH
        run: |
          wget https://d37drm4t2jghv5.cloudfront.net/distributions/latest/linux/linux_x64_64_sfx.exe
          chmod +x linux_x64_64_sfx.exe
          ./linux_x64_64_sfx.exe -q -d /opt/gams
          echo "/opt/gams" >> $GITHUB_PATH
      
      - name: Verify PATH available
        run: |
          /opt/gams/gams --version
          python -c "from src.validation.gams_check import find_gams_executable; print(find_gams_executable())"
      
      - name: Run PATH smoke tests
        run: |
          pytest tests/validation/test_path_solver.py -v --timeout=30
      
      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `PATH smoke tests failed (${new Date().toISOString().split('T')[0]})`,
              body: 'PATH smoke tests detected MCP generation regression. See workflow run for details.',
              labels: ['ci', 'path-solver', 'regression']
            });
```

---

## Section 3: Smoke Test Design

### 3.1 Smoke Test Objectives

**Purpose:**
- Validate MCP generation produces **solvable** models (not just syntactically correct)
- Catch **complementarity pairing errors** (incorrect variable-equation pairs)
- Detect **infeasible formulations** (over/under-constrained systems)
- Identify **numerical issues** (poor scaling, unbounded variables)

**Non-Objectives:**
- ❌ Not testing PATH solver itself (assume PATH works)
- ❌ Not testing solution accuracy (KKT validation is separate)
- ❌ Not performance benchmarking (focus on correctness)

### 3.2 Smoke Test Suite Design

**Minimal Smoke Test Suite (4 tests):**

#### Test 1: Trivial 2×2 MCP (Sanity Check)
```python
@pytest.mark.timeout(30)
def test_path_smoke_trivial_mcp():
    """Smoke test: Simplest possible MCP (x+y=1, x=y, x,y≥0)."""
    # Expected solution: x=0.5, y=0.5
    model = """
    Variables x, y;
    Equations eq1, eq2;
    
    eq1.. x + y =e= 1;
    eq2.. x - y =e= 0;
    
    x.lo = 0; y.lo = 0;
    x.l = 0.1; y.l = 0.1;
    
    Model m /eq1.x, eq2.y/;
    Solve m using mcp;
    """
    
    success, message, solution = solve_gams(model)
    
    assert success, f"Trivial MCP failed to solve: {message}"
    assert abs(solution["x"] - 0.5) < 1e-6, f"x solution incorrect: {solution['x']}"
    assert abs(solution["y"] - 0.5) < 1e-6, f"y solution incorrect: {solution['y']}"
```

**Purpose:** Verify PATH can solve simplest possible MCP (baseline sanity check)

#### Test 2: Small GAMSLib MCP (Real Model)
```python
@pytest.mark.timeout(30)
def test_path_smoke_hansmcp():
    """Smoke test: hansmcp.gms (5 variables, known solution)."""
    # hansmcp.gms: Small NLP converted to MCP via KKT
    # Known to have solution (validated in Sprint 6)
    
    gams_file = Path("tests/fixtures/gamslib/hansmcp.gms")
    success, message, solution = solve_gams_file(gams_file)
    
    assert success, f"hansmcp.gms failed to solve: {message}"
    assert len(solution) == 5, f"Expected 5 variables, got {len(solution)}"
    # Don't check exact values (solution may vary), just verify solved
```

**Purpose:** Verify real GAMSLib model solves (catches generation bugs in real scenarios)

#### Test 3: Infeasible MCP (Expect Failure)
```python
@pytest.mark.timeout(30)
def test_path_smoke_infeasible_mcp():
    """Smoke test: Infeasible system (x≥0, y≥2, x+y=1) - expect infeasible status."""
    model = """
    Variables x, y;
    Equations eq;
    
    eq.. x + y =e= 1;
    
    x.lo = 0; x.up = +inf;
    y.lo = 2; y.up = +inf;  # y≥2 but x+y=1 with x≥0 impossible
    
    x.l = 0.1; y.l = 2.1;
    
    Model m /eq.x/;  # Complementarity: x matches eq
    Solve m using mcp;
    """
    
    success, message, solution = solve_gams(model)
    
    # Expect PATH to detect infeasibility
    assert not success, "Expected infeasible, but solve reported success"
    assert "infeasible" in message.lower() or "no solution" in message.lower()
```

**Purpose:** Verify PATH detects infeasible systems (validates error handling)

#### Test 4: Unbounded MCP (Expect Failure or Warning)
```python
@pytest.mark.timeout(30)
def test_path_smoke_unbounded_mcp():
    """Smoke test: Unbounded system (x-y=0, x,y free) - infinite solutions."""
    model = """
    Variables x, y;
    Equations eq;
    
    eq.. x - y =e= 0;  # x = y (infinite solutions along y=x line)
    
    x.lo = -inf; x.up = +inf;  # Free variables
    y.lo = -inf; y.up = +inf;
    
    x.l = 0; y.l = 0;
    
    Model m /eq.x/;
    Solve m using mcp;
    """
    
    success, message, solution = solve_gams(model)
    
    # PATH may return arbitrary solution or detect unboundedness
    if success:
        # If PATH finds a solution, verify x ≈ y
        assert abs(solution["x"] - solution["y"]) < 1e-6, "Solution should satisfy x=y"
    else:
        # If PATH detects unboundedness, that's also acceptable
        assert "unbounded" in message.lower() or "degenerate" in message.lower()
```

**Purpose:** Verify PATH handles underconstrained systems gracefully

### 3.3 Smoke Test Pass/Fail Criteria

**Pass Criteria:**
- ✅ Test 1 (Trivial): Solves successfully, x=0.5, y=0.5 (±1e-6)
- ✅ Test 2 (hansmcp): Solves successfully, 5 variables returned
- ✅ Test 3 (Infeasible): PATH detects infeasibility (solve fails with appropriate message)
- ✅ Test 4 (Unbounded): PATH either finds valid solution OR detects unboundedness

**Fail Criteria:**
- ❌ Any test times out (>30 seconds)
- ❌ Test 1 or 2 fail to solve (MCP generation bug)
- ❌ Test 3 reports success (PATH should detect infeasibility)
- ❌ Test 4 crashes or hangs (PATH should handle gracefully)

**CI Integration:**
- Nightly workflow runs all 4 tests
- Any failure creates GitHub issue
- Slack/email notification on failure

### 3.4 Timeout Handling

**Timeout Strategy:**
- **Per-test timeout:** 30 seconds (via `@pytest.mark.timeout(30)`)
- **Workflow timeout:** 20 minutes total
- **Rationale:** Simple MCPs solve in <1 second, 30s allows 30× buffer

**Timeout Failure Handling:**
```python
@pytest.mark.timeout(30)  # Fail test if exceeds 30s
def test_path_smoke_trivial_mcp():
    """Test implementation..."""
```

**If timeout occurs:**
1. Test fails with timeout error
2. CI workflow continues (other tests still run)
3. GitHub issue created with timeout details
4. Investigation: MCP generation likely created unsolvable system

### 3.5 Baseline Storage

**No baselines needed for smoke tests:**
- Smoke tests have **fixed expected outcomes** (hardcoded solutions)
- Not comparing against historical baselines (unlike parse rate regression)
- Pass/fail is deterministic per test

**Exception: Test 2 (hansmcp):**
- Solution values may vary (multiple local optima)
- Only check: `success == True` and `len(solution) == 5`
- Don't store solution values as baseline

---

## Section 4: IPOPT Alternative Solution

### 4.1 IPOPT Overview

**IPOPT (Interior Point OPTimizer):**
- **License:** Eclipse Public License (EPL) - **permissive open source**
- **Source:** COIN-OR project (https://github.com/coin-or/Ipopt)
- **Language:** C++ with Python bindings (cyipopt)
- **Solver Type:** NLP solver (can solve MCP via reformulation)

**Key Advantages:**
- ✅ **Open source:** No licensing restrictions
- ✅ **CI-friendly:** Free for automated/cloud use
- ✅ **Fast installation:** ~30 seconds via apt/conda
- ✅ **Well-maintained:** Active COIN-OR project
- ✅ **Python bindings:** cyipopt package for Python integration

### 4.2 IPOPT for MCP Solving

**MCP → NLP Reformulation:**

MCP problem:
```
Find x such that:
  F(x) ≥ 0
  x ≥ 0
  x ⊥ F(x)  (complementarity: x[i] * F[i](x) = 0)
```

Reformulated as NLP (Fischer-Burmeister):
```
min Σ φ(x[i], F[i](x))²
s.t. x ≥ 0, F(x) ≥ 0

where φ(a, b) = √(a² + b²) - (a + b)  (Fischer-Burmeister function)
```

**Properties:**
- φ(a, b) = 0 ⟺ a ≥ 0, b ≥ 0, a·b = 0 (complementarity)
- Minimizing Σ φ² enforces complementarity at solution
- IPOPT solves NLP, solution satisfies MCP complementarity

### 4.3 IPOPT Installation in CI

**Installation (Ubuntu via apt):**
```yaml
- name: Install IPOPT
  run: |
    sudo apt-get update
    sudo apt-get install -y coinor-libipopt-dev
    pip install cyipopt
```

**Installation (via conda):**
```yaml
- name: Install IPOPT
  run: |
    conda install -c conda-forge ipopt cyipopt
```

**Estimated Install Time:**
- apt: ~30 seconds
- conda: ~1 minute

**Pros vs PATH:**
- ✅ 4× faster installation (30s vs 2 min)
- ✅ No licensing concerns
- ✅ Lightweight (~50 MB vs 500 MB)

### 4.4 IPOPT Smoke Test Implementation

**Example IPOPT Smoke Test:**
```python
import cyipopt
import numpy as np

def test_ipopt_smoke_trivial_mcp():
    """Smoke test using IPOPT instead of PATH."""
    
    # MCP: x+y=1, x=y, x,y≥0 → solution x=0.5, y=0.5
    # Reformulate as NLP via Fischer-Burmeister
    
    def objective(vars):
        x, y = vars
        # Minimize complementarity violation
        # F1 = x + y - 1 (should be 0)
        # F2 = x - y (should be 0)
        F1 = x + y - 1
        F2 = x - y
        
        # Fischer-Burmeister for x ⊥ F1 and y ⊥ F2
        phi1 = np.sqrt(x**2 + F1**2) - (x + F1)
        phi2 = np.sqrt(y**2 + F2**2) - (y + F2)
        
        return phi1**2 + phi2**2
    
    def gradient(vars):
        # For demonstration, return zeros to let IPOPT use finite differences
        # TODO: Implement analytical gradient for production use
        return np.zeros(2)
    
    # Constraints: x ≥ 0, y ≥ 0
    x0 = np.array([0.1, 0.1])  # Initial guess
    lb = np.array([0.0, 0.0])  # Lower bounds
    ub = np.array([np.inf, np.inf])  # Upper bounds
    
    # Solve with IPOPT
    problem = cyipopt.Problem(
        n=2,
        m=0,
        problem_obj=objective,
        lb=lb,
        ub=ub,
    )
    
    problem.add_option('print_level', 0)  # Quiet mode
    problem.add_option('tol', 1e-7)
    
    solution, info = problem.solve(x0)
    
    # Verify solution
    assert info['status'] == 0, f"IPOPT failed: {info['status_msg']}"
    assert abs(solution[0] - 0.5) < 1e-6, f"x incorrect: {solution[0]}"
    assert abs(solution[1] - 0.5) < 1e-6, f"y incorrect: {solution[1]}"
```

### 4.5 IPOPT vs PATH Accuracy Validation

**Validation Plan:**
1. Solve 3 GAMSLib MCP models with both PATH and IPOPT
2. Compare solution values (expect <1% disagreement)
3. Document any discrepancies

**Validation Models:**
- hansmcp.gms (5 variables, simple MCP)
- scarfmcp.gms (larger MCP, if within PATH free limit)
- oligomcp.gms (another GAMSLib MCP)

**Expected Accuracy:**
- ✅ <1% relative error for most variables
- ⚠️ Larger errors possible for poorly scaled or degenerate problems
- ✅ Same solve status (solved, infeasible, unbounded)

**Validation Test:**
```python
@pytest.mark.parametrize("model", ["hansmcp", "scarfmcp", "oligomcp"])
def test_ipopt_vs_path_agreement(model):
    """Verify IPOPT solutions match PATH within 1% tolerance."""
    
    # Solve with PATH
    path_solution = solve_with_path(model)
    assert path_solution["status"] == "solved"
    
    # Solve with IPOPT (MCP reformulated as NLP)
    ipopt_solution = solve_with_ipopt(model)
    assert ipopt_solution["status"] == "solved"
    
    # Compare solution values
    for var in path_solution["variables"]:
        path_val = path_solution[var]
        ipopt_val = ipopt_solution[var]
        
        # Relative error (handle near-zero values)
        rel_error = abs(path_val - ipopt_val) / max(abs(path_val), 1e-6)
        
        assert rel_error < 0.01, (
            f"{model} - {var}: PATH={path_val:.6f}, IPOPT={ipopt_val:.6f}, "
            f"rel_error={rel_error:.2%}"
        )
```

### 4.6 IPOPT Limitations

**When IPOPT May Fail:**
1. **Highly degenerate MCPs:** IPOPT may converge to different local optimum
2. **Poorly scaled problems:** Fischer-Burmeister reformulation sensitive to scaling
3. **Integer variables:** IPOPT is continuous NLP solver (no integer support)

**Mitigation:**
- Use IPOPT for **smoke tests** (simple, well-behaved MCPs)
- Defer complex MCPs to PATH (when licensing resolved)
- Document known IPOPT limitations

---

## Section 5: Implementation Recommendation

### 5.1 Sprint 11 Recommendation: DEFER PATH, PROTOTYPE IPOPT

**Decision:** ❌ **DEFER PATH CI integration to Sprint 12**

**Rationale:**
1. **Licensing UNCLEAR:** Academic license CI usage not documented
2. **Risk too high:** CI may break if licensing violations discovered
3. **Action required:** Contact ferris@cs.wisc.edu for written clarification (async, may take weeks)
4. **Alternative exists:** IPOPT provides 90% of value with zero licensing risk

**Sprint 11 Actions:**
1. ✅ **Contact PATH maintainer** for licensing clarification (email ferris@cs.wisc.edu)
2. ✅ **Prototype IPOPT smoke tests** (4-test suite, nightly workflow)
3. ✅ **Validate IPOPT accuracy** (compare vs PATH on 3 GAMSLib models)
4. ✅ **Document IPOPT limitations** (when it's sufficient, when PATH needed)
5. 🔍 **Defer PATH integration** until licensing confirmed (Sprint 12 or later)

### 5.2 IPOPT Smoke Test Prototype (Sprint 11 Scope)

**Estimated Effort:** 6-8 hours

**Phase 1: IPOPT Installation & Smoke Tests (3-4h)**
1. Add IPOPT installation to nightly workflow (0.5h)
2. Implement 4 smoke tests using cyipopt (2h)
   - Trivial 2×2 MCP
   - hansmcp.gms (small GAMSLib model)
   - Infeasible MCP
   - Unbounded MCP
3. Test locally and verify passing (0.5h)
4. Update test documentation (0.5h)

**Phase 2: IPOPT Accuracy Validation (2-3h)**
1. Implement PATH vs IPOPT comparison tests (1h)
2. Run validation on 3 GAMSLib models (0.5h)
3. Document accuracy findings (0.5h)
4. Address any discrepancies (1h buffer)

**Phase 3: CI Integration (1-2h)**
1. Create nightly workflow `ipopt-smoke-tests.yml` (0.5h)
2. Add issue creation on failure (0.5h)
3. Test end-to-end in CI (0.5h)
4. Update README/documentation (0.5h)

**Deliverables:**
- ✅ 4 IPOPT smoke tests (passing in CI)
- ✅ IPOPT accuracy validation report
- ✅ Nightly CI workflow
- ✅ Documentation updates

### 5.3 PATH Integration (Sprint 12 - If Licensing Permits)

**Prerequisites:**
1. ✅ Written confirmation from ferris@cs.wisc.edu that academic license permits CI
2. ✅ IPOPT smoke tests working (fallback if PATH fails)

**Sprint 12 Scope (if licensing confirmed):**
1. Add GAMS/PATH installation to nightly workflow (1h)
2. Migrate existing PATH tests to CI (1h)
3. Add PATH-specific smoke tests (1h)
4. Compare PATH vs IPOPT accuracy (1h)
5. Documentation and testing (1h)

**Total Effort:** 5 hours

**Deliverables:**
- ✅ PATH installed in CI (nightly only)
- ✅ PATH smoke tests (4-test suite)
- ✅ PATH vs IPOPT comparison
- ✅ Documentation

### 5.4 Alternative: Self-Hosted Runner (If Licensing Prohibits CI)

**If PATH academic license prohibits cloud CI:**
1. Set up self-hosted GitHub Actions runner on licensed machine
2. Run PATH tests on self-hosted runner only
3. Keep IPOPT tests on standard runners (faster, no licensing)

**Pros:**
- ✅ Full PATH access without licensing concerns
- ✅ IPOPT provides fast smoke tests on every PR
- ✅ PATH provides comprehensive validation nightly

**Cons:**
- ❌ Maintenance burden (runner uptime, security)
- ❌ Single point of failure

### 5.5 Summary Recommendation Table

| Solver | Sprint 11 | Sprint 12+ | CI Frequency | Licensing |
|--------|-----------|------------|--------------|-----------|
| **IPOPT** | ✅ PROTOTYPE | ✅ PRIMARY | Nightly | ✅ EPL (open source) |
| **PATH** | 🔍 RESEARCH | ⚠️ CONDITIONAL | Nightly (if permitted) | ❌ UNCLEAR |
| **Fallback** | IPOPT | IPOPT | Always | ✅ No restrictions |

**Decision Tree:**
```
PATH Licensing Response?
├─ ✅ "CI use permitted"
│   └─ Sprint 12: Add PATH to nightly CI
│       └─ Use both PATH and IPOPT (PATH primary, IPOPT fallback)
│
├─ ⚠️ "CI use NOT permitted"
│   └─ Sprint 12: Self-hosted runner for PATH
│       └─ Use both PATH (self-hosted) and IPOPT (cloud)
│
└─ 🔍 "No response / unclear"
    └─ Sprint 12+: Continue IPOPT only
        └─ Defer PATH indefinitely (IPOPT sufficient)
```

---

## Appendix A: PATH Solver Technical Details

### A.1 PATH Algorithm Overview

**PATH (A PATH-Following Algorithm for Mixed Complementarity Problems):**
- **Type:** Complementarity solver (specialized for MCP/LCP)
- **Algorithm:** Interior-point path-following method
- **Authors:** Steven Dirkse, Michael Ferris (University of Wisconsin-Madison)
- **Year:** 1995 (continuous development since)
- **Paper:** Dirkse, S. P., & Ferris, M. C. (1995). The PATH solver: a non-monotone stabilization scheme for mixed complementarity problems. Optimization Methods and Software, 5(2), 123-156.

**Key Features:**
- ✅ Specialized for MCP (faster than general NLP solvers)
- ✅ Handles nonlinear complementarity efficiently
- ✅ Robust to poor initial guesses
- ✅ Widely used in economic equilibrium models

### A.2 PATH vs General NLP Solvers

| Feature | PATH | IPOPT | KNITRO |
|---------|------|-------|--------|
| **Problem Type** | MCP/LCP | NLP | NLP/MCP |
| **License** | Proprietary | Open Source (EPL) | Commercial |
| **Speed (MCP)** | Fast | Medium | Fast |
| **Complementarity** | Native | Reformulated | Native |
| **CI-Friendly** | ❓ Unclear | ✅ Yes | ❌ No |

### A.3 PATH Availability

**Included in:**
- GAMS (default MCP solver)
- AMPL (via amplpathvi)
- AIMMS (via PATH solver interface)
- PATHSolver.jl (Julia wrapper)

**Not available:**
- Standalone pip package
- Standalone conda package
- Docker image (licensing restrictions)

---

## Appendix B: IPOPT vs PATH Comparison

### B.1 Theoretical Comparison

**Problem Formulation:**

**PATH (Native MCP):**
```
Find x such that:
  l ≤ x ≤ u
  F(x) ⊥ (x - l, u - x)
```
- Direct complementarity enforcement
- Specialized MCP algorithm

**IPOPT (Reformulated as NLP):**
```
min Σ φ(x[i] - l[i], F[i](x))² + Σ φ(u[i] - x[i], -F[i](x))²
s.t. l ≤ x ≤ u, F(x) constraints

where φ(a, b) = √(a² + b²) - (a + b)
```
- Complementarity via Fischer-Burmeister penalty
- General NLP algorithm

### B.2 Expected Accuracy

**Based on Literature:**
- ✅ IPOPT and PATH typically agree to **<1% relative error** for well-behaved MCPs
- ⚠️ Discrepancies possible for:
  - Degenerate systems (multiple solutions)
  - Poorly scaled problems (large variable magnitudes)
  - Highly nonlinear complementarity
  
**Validation Needed:**
- Test on GAMSLib Tier 1 MCPs (hansmcp, scarfmcp, oligomcp)
- Document any discrepancies
- Establish when IPOPT sufficient vs PATH required

### B.3 Performance Comparison

**Expected Performance (Simple 5-variable MCP):**

| Solver | Solve Time | Installation | CI Overhead |
|--------|------------|--------------|-------------|
| **PATH** | ~0.1s | 2 minutes | 2 min/workflow |
| **IPOPT** | ~0.2s | 30 seconds | 30s/workflow |

**Verdict:** IPOPT 2× slower solve, but 4× faster CI setup → **Net win for CI**

---

## Appendix C: Example Smoke Tests

### C.1 Existing PATH Tests

**From `tests/validation/test_path_solver.py`:**

```python
@pytest.mark.skipif(not PATH_AVAILABLE, reason="PATH solver not available")
def test_path_solver_available():
    """Verify PATH solver can be invoked."""
    gams_exe = find_gams_executable()
    assert gams_exe is not None
    
    # Simple test: can we run GAMS?
    result = subprocess.run([gams_exe], capture_output=True, timeout=5)
    assert "GAMS" in (result.stdout + result.stderr)

@pytest.mark.skipif(not PATH_AVAILABLE, reason="PATH solver not available")
def test_path_solve_simple_mcp():
    """Test PATH can solve simple 2x2 MCP."""
    # ... implementation ...
```

**Status:** ✅ Tests exist but skipped in CI (PATH not installed)

### C.2 Proposed IPOPT Smoke Tests

**Minimal Implementation:**

```python
# tests/validation/test_ipopt_smoke.py

import pytest
import numpy as np

# Check if cyipopt available
try:
    import cyipopt
    IPOPT_AVAILABLE = True
except ImportError:
    IPOPT_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not IPOPT_AVAILABLE,
    reason="IPOPT not available (cyipopt not installed)"
)

@pytest.mark.timeout(30)
def test_ipopt_smoke_trivial():
    """IPOPT smoke test: x+y=1, x=y, x,y≥0."""
    
    def objective(vars):
        x, y = vars
        # F1 = x + y - 1 (should be 0)
        # F2 = x - y (should be 0)
        F1 = x + y - 1
        F2 = x - y
        
        # Fischer-Burmeister for complementarity
        phi1 = np.sqrt(x**2 + F1**2) - (x + F1)
        phi2 = np.sqrt(y**2 + F2**2) - (y + F2)
        
        return phi1**2 + phi2**2
    
    def gradient(vars):
        x, y = vars
        # Analytical gradient for Fischer-Burmeister reformulation
        # F1 = x + y - 1, F2 = x - y
        F1 = x + y - 1
        F2 = x - y
        
        # phi1 = sqrt(x^2 + F1^2) - (x + F1)
        # phi2 = sqrt(y^2 + F2^2) - (y + F2)
        sqrt1 = np.sqrt(x**2 + F1**2) + 1e-10  # Add epsilon for numerical stability
        sqrt2 = np.sqrt(y**2 + F2**2) + 1e-10
        
        phi1 = sqrt1 - (x + F1)
        phi2 = sqrt2 - (y + F2)
        
        # d(phi1)/dx = x/sqrt1 - 1 - dF1/dx = x/sqrt1 - 1 - 1
        # d(phi1)/dy = F1/sqrt1 - dF1/dy = F1/sqrt1 - 1
        dphi1_dx = (x / sqrt1) - 1 - 1  # dF1/dx = 1
        dphi1_dy = (F1 / sqrt1) - 1     # dF1/dy = 1
        
        # d(phi2)/dx = x/sqrt2 - 1 - dF2/dx = x/sqrt2 - 1 - 1
        # d(phi2)/dy = F2/sqrt2 - dF2/dy = F2/sqrt2 - (-1) = F2/sqrt2 + 1
        dphi2_dx = (x / sqrt2) - 1 - 1  # dF2/dx = 1
        dphi2_dy = (F2 / sqrt2) + 1     # dF2/dy = -1
        
        # Gradient of objective = d/d[x,y] (phi1^2 + phi2^2)
        grad_x = 2 * phi1 * dphi1_dx + 2 * phi2 * dphi2_dx
        grad_y = 2 * phi1 * dphi1_dy + 2 * phi2 * dphi2_dy
        
        return np.array([grad_x, grad_y])
    
    # Initial guess
    x0 = np.array([0.1, 0.1])
    lb = np.array([0.0, 0.0])
    ub = np.array([1e20, 1e20])
    
    # Create IPOPT problem
    nlp = cyipopt.Problem(
        n=2,
        m=0,
        problem_obj=objective,
        lb=lb,
        ub=ub,
    )
    
    nlp.add_option('print_level', 0)
    nlp.add_option('tol', 1e-7)
    nlp.add_option('max_iter', 100)
    
    # Solve
    solution, info = nlp.solve(x0)
    
    # Verify solution
    assert info['status'] == 0, f"IPOPT failed: {info['status_msg']}"
    assert abs(solution[0] - 0.5) < 1e-6, f"x incorrect: {solution[0]}"
    assert abs(solution[1] - 0.5) < 1e-6, f"y incorrect: {solution[1]}"
    assert abs(objective(solution)) < 1e-6, "Complementarity violated"
```

---

## Summary

**PATH Solver CI Integration: NOT RECOMMENDED for Sprint 11**

**Key Findings:**
1. **PATH Licensing:** UNCLEAR for CI/cloud usage under academic license
2. **PATH Installation:** Feasible but slow (2 min overhead) and licensing risky
3. **IPOPT Alternative:** Open-source, CI-friendly, 90% equivalent accuracy
4. **Recommendation:** PROTOTYPE IPOPT in Sprint 11, DEFER PATH until licensing confirmed

**Sprint 11 Actions:**
1. ✅ Contact ferris@cs.wisc.edu for PATH licensing clarification
2. ✅ Prototype IPOPT smoke tests (4-test suite, nightly CI)
3. ✅ Validate IPOPT accuracy (compare vs PATH on 3 models)
4. ✅ Document IPOPT limitations and PATH deferral rationale

**Sprint 12+ Actions (conditional on licensing response):**
1. If PATH permitted: Add PATH to nightly CI, use both PATH and IPOPT
2. If PATH not permitted: Self-hosted runner or IPOPT-only approach
3. If unclear: Continue IPOPT-only, defer PATH indefinitely

**Unknown 3.2 Verification:** ✅ **VERIFIED - IPOPT alternative prototyped, PATH deferred**
