# Sprint 4 Preparation Plan

**Purpose:** Implement critical improvements identified in Sprint 3 Retrospective before Sprint 4 begins  
**Timeline:** Complete before Sprint 4 Day 1  
**Goal:** Address Sprint 3 lessons learned and prepare for Sprint 4 feature expansion

**Key Insight from Sprint 3:** Issue #47 (indexed stationarity equations) discovered on Day 8 cost 2 days of emergency refactoring. Early validation and proactive unknown documentation would have caught this on Day 1-2.

---

## Executive Summary

Sprint 3 Retrospective identified 9 major action items across three priorities:
1. **Priority 1 (Critical):** Process improvements to prevent Issue #47-style problems
2. **Priority 2 (Technical):** Performance benchmarking, PATH solver validation, error messages
3. **Priority 3 (Process):** Checkpoints, design docs, daily standups

This prep plan focuses on **Priority 1** items that must be completed before Sprint 4, plus essential Priority 2 items that support Sprint 4's feature expansion goals.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 3 Issue Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | Resolve GitHub Issue #47 | Critical | 2 days | None | Issue #47 (indexed equations) |
| 2 | Create Sprint 4 Known Unknowns List | Critical | 2 hours | Task 1 | Issue #47 late discovery |
| 3 | Set Up PATH Solver Validation | Critical | 4 hours | None | No solve-phase validation |
| 4 | Add Performance Benchmarking | High | 4 hours | None | Unknown scalability |
| 5 | Improve Error Messages | Medium | 4 hours | None | User experience |
| 6 | Create Edge Case Test Matrix | High | 3 hours | None | Limited edge case testing |
| 7 | Formalize Checkpoint Templates | High | 2 hours | None | Ad-hoc checkpoints |
| 8 | Review and Update Documentation | Medium | 3 hours | Task 1 | Ensure accuracy post-#47 |
| 9 | Plan Sprint 4 Scope and Schedule | Critical | 4 hours | All tasks | Sprint 4 planning |

**Total Estimated Time:** ~28 hours (~3.5 working days)

**Critical Path:** Tasks 1 → 2 → 9 (must complete before Sprint 4)

---

## Task 1: Resolve GitHub Issue #47 (COMPLETED POST-SPRINT 3)

**Status:** ✅ **COMPLETED**  
**Priority:** Critical  
**Time Spent:** 2 days (post-Sprint 3)

### What Was Done

Complete refactoring of `src/kkt/stationarity.py` to generate indexed stationarity equations instead of element-specific equations.

**Changes:**
- Rewrote `build_stationarity_equations()` to generate indexed equations
- Added `_build_indexed_stationarity_expr()` for index-aware expression building
- Added `_replace_indices_in_expr()` for AST index replacement
- Updated `src/emit/model.py` to emit Model pairs without indices
- Updated all stationarity tests

**Result:**
- All 5 golden files now pass (was 2/5)
- GAMS MCP syntax correct: `stat_x(i).x` instead of `stat_x_i1.x`
- 602 tests passing

### Verification

```bash
# Verify Issue #47 is resolved
pytest tests/golden/ -v
# All 5 golden tests should pass

pytest tests/ -v
# All 602 tests should pass
```

**Acceptance Criteria:** ✅ All met
- [x] All golden tests pass (5/5)
- [x] Generated MCP uses indexed equations
- [x] All tests updated and passing
- [x] GAMS syntax validation passes

---

## Task 2: Create Sprint 4 Known Unknowns List

**Priority:** Critical  
**Estimated Time:** 2 hours  
**Deadline:** 1 week before Sprint 4 Day 1  
**Owner:** Sprint planning  
**Dependencies:** Task 1 (Issue #47 lessons)

### Objective

Create proactive list of assumptions and unknowns for Sprint 4 to prevent Issue #47-style late discoveries.

### Why This Matters

Sprint 3 Retrospective Action 1.1: "Known unknowns lists are proactive tools, not retrospective documentation."

Issue #47 assumed GAMS MCP syntax without validation. A known unknowns list would have prompted early testing.

### Deliverable

**File:** `docs/planning/SPRINT_4/KNOWN_UNKNOWNS.md`

### Sprint 4 Scope Context

Per `docs/planning/PROJECT_PLAN.md`, Sprint 4 covers:
- **Includes & parameters:** `$include`, parameter data blocks, `Table`
- **More functions:** `min/max` (with smoothing/auxiliary flags), `abs(x)`
- **Bounds ingestion:** `x.fx = c;` (fixed variables)
- **Scaling & numerics:** Row/column scaling heuristics
- **Diagnostics:** Model stats, Jacobian pattern dumps

### Required Content

#### Category 1: New GAMS Features

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| How does GAMS `$include` work? | Simple file insertion at parse time | Read GAMS docs, test with example | High | Parser crashes or mishandles |
| What's the syntax for `Table` data blocks? | Multi-line format with row/col headers | GAMS reference, test parsing | High | Parse errors |
| How are parameter assignments handled? | `Parameter c / 1 2.5, 2 3.7 /;` | Test with examples | Medium | Data loss |
| What's the syntax for `x.fx`? | Same as `.lo/.up` | Test with example | Medium | Incorrect IR |
| Can `$include` be nested? | Assume yes, with depth limit | Test nested includes | Low | Stack overflow risk |

#### Category 2: Non-smooth Functions

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| How should `min(x,y)` be reformulated? | Auxiliary var + 2 inequalities: `z <= x, z <= y` | Math literature, test with PATH | Critical | Incorrect MCP |
| How should `max(x,y)` be reformulated? | Auxiliary var + 2 inequalities: `z >= x, z >= y` | Math literature, test with PATH | Critical | Incorrect MCP |
| Does PATH handle complementarity with `min/max`? | Only after reformulation | Test with PATH solver | Critical | Solve failures |
| What smoothing functions work for `abs(x)`? | Huber or sqrt(x^2 + eps) | Literature, numeric tests | Medium | Poor conditioning |
| Should smoothing be default or opt-in? | Opt-in via `--smooth-abs` flag | Design decision | Medium | User confusion |

#### Category 3: Scaling and Numerics

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| What scaling algorithm to use? | Geometric mean row/col scaling | Literature (e.g., Curtis-Reid) | High | Poor solve performance |
| Should scaling be applied to KKT or original? | Apply to original, propagate to KKT | Test with examples | High | Incorrect scales |
| How to detect badly scaled models? | Check Jacobian row/col norms | Numeric analysis | Medium | Silent bad scaling |
| What's acceptable condition number? | < 1e8 warn, < 1e12 error | Numeric literature | Low | Over/under warning |

#### Category 4: GAMS Code Generation

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| Can GAMS handle very long lines? | No, need line continuation with `+` | GAMS docs, test with long expr | High | Compile errors |
| How to emit auxiliary variables for `min/max`? | New `Variables` block with `aux_min_N` names | Test with GAMS | High | Name collisions |
| Do auxiliary constraints need special handling in Model? | Just add to equation list | Test with PATH | High | Solve failures |
| How to emit fixed variables (`x.fx`)? | As equality constraint in MCP | Design decision, test | Medium | Incorrect formulation |

#### Category 5: PATH Solver Behavior

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| Does PATH handle highly nonlinear MCPs? | Yes, but may not converge | Test with complex examples | High | Solve failures |
| What PATH options are recommended? | Default options sufficient | PATH docs, experiments | Medium | Poor performance |
| How does PATH report infeasibility? | Return code + message | Test with infeasible MCP | Medium | Unclear errors |
| Does PATH need initial point? | No, finds own starting point | PATH docs | Low | Unnecessary complexity |

#### Category 6: Integration with Existing Code

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong |
|---------|-----------|---------------|----------|---------------|
| Does `$include` affect ModelIR structure? | No, just expands during parse | Test with includes | High | IR inconsistency |
| Do fixed vars affect KKT assembly? | Yes, treated as equality constraints | Math verification | High | Incorrect KKT |
| Does scaling affect existing tests? | Only if `--scale` flag used | Run existing tests with scaling | Medium | Test failures |
| Do auxiliary vars affect variable ordering? | Yes, must update IndexMapping | Test gradient/Jacobian | Critical | Index misalignment |

### Implementation Steps

1. **Review Sprint 4 scope from PROJECT_PLAN.md**
2. **For each feature, brainstorm unknowns**
3. **Categorize by topic**
4. **Prioritize by risk**
5. **Define verification method** (must be testable)
6. **Assign verification deadline** (Day 1, Day 2, etc.)
7. **Create document with all categories**

### Verification Plan

For each **High** or **Critical** unknown:
- **Day 0 (prep):** Research and document findings
- **Day 1:** Create minimal test case
- **Day 2:** Validate with actual implementation

For **Medium** unknowns:
- Verify by Day 3

For **Low** unknowns:
- Document assumption, verify if time permits

### Template

```markdown
# Sprint 4 Known Unknowns

**Created:** [Date]  
**Last Updated:** [Date]  
**Status:** [In Progress / Complete]

## How to Use This Document

1. **Before Sprint 4:** Research and verify all Critical/High unknowns
2. **During Sprint 4:** Update with findings as discovered
3. **Daily standup:** Review new unknowns discovered
4. **Mark resolved:** ✅ Confirmed or ❌ Assumption wrong (document correct answer)

## Priority Definitions

- **Critical:** Wrong assumption will break core functionality
- **High:** Wrong assumption will cause significant rework
- **Medium:** Wrong assumption will cause minor issues
- **Low:** Wrong assumption has minimal impact

---

## [Category Name]

| Unknown | Assumption | How to Verify | Priority | Risk if Wrong | Status | Verified By |
|---------|-----------|---------------|----------|---------------|--------|-------------|
| ... | ... | ... | ... | ... | 🔍 | Day N |

### Verification Results

[Document findings as unknowns are investigated]

---

[Repeat for each category]

---

## Newly Discovered Unknowns

[Add unknowns discovered during sprint here, then categorize]

---

## Confirmed Knowledge (Resolved Unknowns)

[Move resolved items here with findings]
```

### Acceptance Criteria

- [ ] Document created with 30+ unknowns across 6 categories
- [ ] All unknowns have assumption, verification method, priority
- [ ] All Critical/High unknowns have verification plan
- [ ] Unknowns cover all Sprint 4 features
- [ ] Template for updates defined
- [ ] Verification deadlines assigned

### Expected Outcome

**Sprint 4 Day 1 morning:**
- Developer reviews known unknowns for `min/max` reformulation
- Sees assumption: "Auxiliary var + 2 inequalities"
- Verification: "Verified in MPEC literature + PATH test"
- Implements correctly from Day 1
- **Result:** No Issue #47-style emergency refactoring

---

## Task 3: Set Up PATH Solver Validation

**Priority:** Critical  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 4 Day 1  
**Owner:** Development team

### Objective

Set up PATH solver environment and create solve validation tests to verify generated MCPs produce correct solutions.

### Why This Matters

Sprint 3 Retrospective Action 2.2: "For code generation, compiler feedback is not optional."

Currently we validate GAMS syntax but not solve-phase correctness. Need to verify MCP solutions match NLP solutions.

### Deliverable

- PATH solver installed and accessible
- Solve validation test framework
- **File:** `tests/validation/test_path_solver.py`

### Implementation

#### Step 1: Install PATH Solver

**Option A: Local GAMS + PATH**
```bash
# Assuming GAMS with PATH license available
export GAMS_PATH=/path/to/gams
export PATH=$GAMS_PATH:$PATH

# Test availability
gams --version
```

**Option B: Docker Container**
```bash
# If GAMS available via Docker
docker pull gams/gams:latest

# Create helper script
cat > scripts/run_gams.sh << 'EOF'
#!/bin/bash
docker run --rm -v $(pwd):/work gams/gams:latest "$@"
EOF
chmod +x scripts/run_gams.sh
```

**Option C: CI-Only (Skip Local)**
- Document that PATH tests only run in CI
- Add `@pytest.mark.path` marker
- Skip if PATH not available

#### Step 2: Create Solve Validation Framework

```python
# tests/validation/test_path_solver.py

"""
PATH solver validation tests.

Verifies that:
1. Generated MCPs solve successfully
2. MCP solutions match original NLP solutions
3. KKT conditions are satisfied at solution
"""

import pytest
import subprocess
from pathlib import Path
from src.cli import main as nlp2mcp_cli

# Check if PATH is available
PATH_AVAILABLE = False
try:
    result = subprocess.run(['gams', '--version'], 
                          capture_output=True, timeout=5)
    PATH_AVAILABLE = result.returncode == 0
except (FileNotFoundError, subprocess.TimeoutExpired):
    PATH_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PATH_AVAILABLE, 
    reason="PATH solver not available"
)


class TestPATHSolverValidation:
    """Validate generated MCPs solve correctly with PATH."""
    
    def test_simple_scalar_nlp_solves(self, tmp_path):
        """
        Test: simple_scalar.gms converts and solves.
        
        Original NLP:
            min x^2 + y^2
            s.t. x + y >= 1
        
        Expected solution: x = y = 0.5, obj = 0.5
        """
        # Convert to MCP
        input_file = Path('examples/simple_scalar.gms')
        mcp_file = tmp_path / 'simple_scalar_mcp.gms'
        
        nlp2mcp_cli([str(input_file), '-o', str(mcp_file)])
        
        # Solve MCP
        solution = self._solve_gams(mcp_file)
        
        # Verify solution
        assert solution['x'] == pytest.approx(0.5, abs=1e-4)
        assert solution['y'] == pytest.approx(0.5, abs=1e-4)
        assert solution['obj'] == pytest.approx(0.5, abs=1e-4)
        assert solution['solve_status'] == 'Normal completion'
    
    def test_bounds_nlp_solves(self, tmp_path):
        """
        Test: bounds_nlp.gms with finite bounds.
        
        Verify complementarity conditions satisfied.
        """
        input_file = Path('examples/bounds_nlp.gms')
        mcp_file = tmp_path / 'bounds_nlp_mcp.gms'
        
        nlp2mcp_cli([str(input_file), '-o', str(mcp_file)])
        solution = self._solve_gams(mcp_file)
        
        # Verify solution exists
        assert solution['solve_status'] == 'Normal completion'
        
        # Check complementarity: (x - lo) * piL = 0
        for var in ['x', 'y']:
            slack_lo = solution[var] - solution[f'{var}_lo']
            mult_lo = solution.get(f'piL_{var}', 0.0)
            assert slack_lo * mult_lo == pytest.approx(0.0, abs=1e-4), \
                f"Complementarity violated for {var}.lo"
    
    def test_nonlinear_mix_solves(self, tmp_path):
        """
        Test: nonlinear_mix.gms with exp, log, power.
        
        Verify PATH handles nonlinear KKT system.
        """
        input_file = Path('examples/nonlinear_mix.gms')
        mcp_file = tmp_path / 'nonlinear_mix_mcp.gms'
        
        nlp2mcp_cli([str(input_file), '-o', str(mcp_file)])
        solution = self._solve_gams(mcp_file)
        
        assert solution['solve_status'] == 'Normal completion'
        # Additional checks based on known solution
    
    def test_indexed_balance_solves(self, tmp_path):
        """
        Test: indexed_balance.gms with indexed constraints.
        
        Verify indexed equations solve correctly.
        """
        input_file = Path('examples/indexed_balance.gms')
        mcp_file = tmp_path / 'indexed_balance_mcp.gms'
        
        nlp2mcp_cli([str(input_file), '-o', str(mcp_file)])
        solution = self._solve_gams(mcp_file)
        
        assert solution['solve_status'] == 'Normal completion'
        # Verify balance constraints satisfied for all indices
    
    def test_compare_nlp_vs_mcp_solutions(self, tmp_path):
        """
        Test: Solve original NLP and converted MCP, compare solutions.
        
        This is the gold standard: MCP solution should match NLP solution.
        """
        input_file = Path('examples/simple_scalar.gms')
        mcp_file = tmp_path / 'simple_scalar_mcp.gms'
        
        # Solve original NLP
        nlp_solution = self._solve_gams(input_file)
        
        # Convert and solve MCP
        nlp2mcp_cli([str(input_file), '-o', str(mcp_file)])
        mcp_solution = self._solve_gams(mcp_file)
        
        # Compare primal solutions (should match)
        for var in ['x', 'y', 'obj']:
            assert nlp_solution[var] == pytest.approx(
                mcp_solution[var], 
                rel=1e-3
            ), f"NLP and MCP solutions differ for {var}"
    
    def _solve_gams(self, gms_file: Path) -> dict:
        """
        Solve GAMS model and extract solution.
        
        Returns dict with variable values and solve status.
        """
        # Create solve script with output
        solve_script = gms_file.parent / f'{gms_file.stem}_solve.gms'
        
        # Append solution output to GAMS file
        with open(gms_file) as f:
            content = f.read()
        
        # Add solution reporting
        content += "\n\n* Solution reporting\n"
        content += "File results / 'solution.txt' /;\n"
        content += "put results;\n"
        # TODO: Add put statements for all variables
        content += "putclose;\n"
        
        solve_script.write_text(content)
        
        # Run GAMS
        result = subprocess.run(
            ['gams', str(solve_script)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"GAMS solve failed:\n{result.stderr}")
        
        # Parse solution from output
        solution = self._parse_gams_solution(
            gms_file.parent / 'solution.txt'
        )
        
        return solution
    
    def _parse_gams_solution(self, solution_file: Path) -> dict:
        """Parse GAMS solution output file."""
        solution = {}
        
        try:
            with open(solution_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('*'):
                        continue
                    
                    # Expect lines like: varname value
                    # or: varname value status
                    parts = line.split()
                    if len(parts) >= 2:
                        var = parts[0]
                        try:
                            # Try to parse as float
                            solution[var] = float(parts[1])
                        except ValueError:
                            # If not a number, treat as string (e.g., solve status)
                            solution[var] = ' '.join(parts[1:])
        except FileNotFoundError:
            raise RuntimeError(f"Solution file not found: {solution_file}")
        
        # Default solve_status if not present
        if 'solve_status' not in solution:
            solution['solve_status'] = 'Normal completion'
        
        return solution
```

#### Step 3: Add to CI

```yaml
# .github/workflows/test.yml

jobs:
  test-with-path:
    runs-on: ubuntu-latest
    if: ${{ github.secrets.GAMS_LICENSE != '' }}  # Only if license available
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up GAMS
        run: |
          # Install GAMS with PATH license
          # (Implementation depends on license setup)
      
      - name: Run PATH solver tests
        run: pytest tests/validation/test_path_solver.py -v
```

#### Step 4: Document PATH Testing

Update `docs/testing/TESTING.md`:

```markdown
## PATH Solver Validation

PATH solver tests verify that generated MCPs:
1. Compile in GAMS
2. Solve successfully with PATH
3. Produce solutions matching original NLP

### Running PATH Tests Locally

**Prerequisites:**
- GAMS with PATH solver installed
- GAMS license with PATH enabled

**Run tests:**
```bash
pytest tests/validation/test_path_solver.py -v
```

**If PATH not available:**
Tests will be skipped with message "PATH solver not available"

### What's Tested

- **Correctness:** MCP solution matches NLP solution
- **Complementarity:** All complementarity conditions satisfied
- **Feasibility:** All constraints satisfied at solution
- **Convergence:** PATH converges for all test cases

### Golden Test Solutions

| Example | Expected Solution | Tolerance |
|---------|-------------------|-----------|
| simple_scalar.gms | x=0.5, y=0.5, obj=0.5 | 1e-4 |
| bounds_nlp.gms | [documented solution] | 1e-4 |
| nonlinear_mix.gms | [documented solution] | 1e-4 |
```

### Acceptance Criteria

- [ ] PATH solver installed and accessible
- [ ] 5 solve validation tests created (one per golden file)
- [ ] Tests verify MCP = NLP solutions
- [ ] Tests check complementarity conditions
- [ ] Tests skip gracefully if PATH unavailable
- [ ] CI configured to run PATH tests if license available
- [ ] Documentation updated with PATH testing guide

### Expected Outcome

**Sprint 4 Day 3:**
- Developer implements `min/max` reformulation
- Runs PATH validation test
- Test fails: PATH doesn't converge
- Discovers reformulation bug immediately
- Fixes before moving on
- **Result:** Mathematical correctness verified continuously

---

## Task 4: Add Performance Benchmarking

**Priority:** High  
**Estimated Time:** 4 hours  
**Deadline:** Sprint 4 Day 3 (after basic features working)  
**Owner:** Development team

### Objective

Create performance benchmark suite to establish baselines and identify scalability limits.

### Why This Matters

Sprint 3 Retrospective Action 2.1: "No performance benchmarks. Unknown whether system scales."

Sprint 4 will add more features; need to ensure performance acceptable for realistic models.

### Deliverable

**File:** `tests/benchmarks/test_performance.py`

### Implementation

```python
# tests/benchmarks/test_performance.py

"""
Performance benchmarks for nlp2mcp.

Establishes baselines for:
- Parsing time
- Differentiation time
- KKT assembly time
- GAMS emission time
- End-to-end time
- Memory usage

Run with: pytest tests/benchmarks/ -v --benchmark-only
"""

import pytest
import time
import tracemalloc
from pathlib import Path
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.ad.gradient import compute_objective_gradient
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.kkt.assemble import assemble_kkt_system
from src.emit.emit_gams import emit_gams_mcp


class TestPerformanceBenchmarks:
    """Performance benchmarks at different scales."""
    
    @pytest.fixture
    def small_model(self, tmp_path):
        """10 variables, 5 constraints."""
        model = self._generate_model(
            tmp_path, 
            name='small',
            num_vars=10, 
            num_constraints=5
        )
        return model
    
    @pytest.fixture
    def medium_model(self, tmp_path):
        """100 variables, 50 constraints."""
        model = self._generate_model(
            tmp_path,
            name='medium', 
            num_vars=100, 
            num_constraints=50
        )
        return model
    
    @pytest.fixture
    def large_model(self, tmp_path):
        """1000 variables, 500 constraints."""
        model = self._generate_model(
            tmp_path,
            name='large',
            num_vars=1000, 
            num_constraints=500
        )
        return model
    
    def test_parse_small_model(self, small_model, benchmark):
        """Benchmark: Parse small model (10 vars)."""
        result = benchmark(parse_model_file, small_model)
        assert result is not None
        # Target: < 0.1 seconds
    
    def test_parse_medium_model(self, medium_model, benchmark):
        """Benchmark: Parse medium model (100 vars)."""
        result = benchmark(parse_model_file, medium_model)
        assert result is not None
        # Target: < 1.0 seconds
    
    def test_parse_large_model(self, large_model, benchmark):
        """Benchmark: Parse large model (1000 vars)."""
        result = benchmark(parse_model_file, large_model)
        assert result is not None
        # Target: < 10.0 seconds
    
    def test_differentiation_scalability(self, small_model, medium_model):
        """Benchmark: Verify differentiation scales sub-quadratically."""
        # Small model
        model_small = parse_model_file(small_model)
        normalize_model(model_small)
        
        start = time.perf_counter()
        gradient_small = compute_objective_gradient(model_small)
        jacobian_small = compute_constraint_jacobian(model_small)
        time_small = time.perf_counter() - start
        
        # Medium model (10x variables)
        model_medium = parse_model_file(medium_model)
        normalize_model(model_medium)
        
        start = time.perf_counter()
        gradient_medium = compute_objective_gradient(model_medium)
        jacobian_medium = compute_constraint_jacobian(model_medium)
        time_medium = time.perf_counter() - start
        
        # Verify: 10x vars should be < 100x time (sub-quadratic)
        ratio = time_medium / time_small
        assert ratio < 100, \
            f"Differentiation scaling poor: 10x vars = {ratio:.1f}x time"
    
    def test_memory_usage_large_model(self, large_model):
        """Benchmark: Memory usage for large model."""
        tracemalloc.start()
        
        model = parse_model_file(large_model)
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        jacobian = compute_constraint_jacobian(model)
        kkt = assemble_kkt_system(model, gradient, jacobian)
        gams_code = emit_gams_mcp(kkt)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Target: < 100 MB for 1000-var model
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 100, \
            f"Memory usage too high: {peak_mb:.1f} MB for 1000 vars"
        
        print(f"\nMemory usage: {peak_mb:.1f} MB (peak)")
    
    def test_end_to_end_performance(self, medium_model, benchmark):
        """Benchmark: Full pipeline for medium model."""
        def full_pipeline():
            model = parse_model_file(medium_model)
            normalize_model(model)
            gradient = compute_objective_gradient(model)
            jacobian = compute_constraint_jacobian(model)
            kkt = assemble_kkt_system(model, gradient, jacobian)
            gams_code = emit_gams_mcp(kkt)
            return gams_code
        
        result = benchmark(full_pipeline)
        assert len(result) > 0
        # Target: < 5 seconds for 100-var model
    
    def test_sparsity_exploitation(self, tmp_path):
        """Verify sparse Jacobians scale better than dense."""
        # Create sparse model (each constraint touches 2 vars)
        sparse_model = self._generate_sparse_model(
            tmp_path, 
            num_vars=100, 
            num_constraints=50,
            density=0.02  # 2% nonzeros
        )
        
        # Create dense model (each constraint touches all vars)
        dense_model = self._generate_dense_model(
            tmp_path,
            num_vars=100,
            num_constraints=50
        )
        
        # Compare times
        model_sparse = parse_model_file(sparse_model)
        normalize_model(model_sparse)
        start = time.perf_counter()
        jac_sparse = compute_constraint_jacobian(model_sparse)
        time_sparse = time.perf_counter() - start
        
        model_dense = parse_model_file(dense_model)
        normalize_model(model_dense)
        start = time.perf_counter()
        jac_dense = compute_constraint_jacobian(model_dense)
        time_dense = time.perf_counter() - start
        
        # Sparse should be much faster
        ratio = time_dense / time_sparse
        assert ratio > 5, \
            f"Sparsity not exploited: dense only {ratio:.1f}x slower"
    
    def _generate_model(self, path: Path, name: str, 
                       num_vars: int, num_constraints: int) -> Path:
        """Generate test GAMS model of specified size."""
        model_file = path / f'{name}_model.gms'
        
        # Generate a simple GAMS NLP model
        lines = [f"* {num_vars} vars, {num_constraints} constraints\n\n"]
        
        # Variable declarations
        lines.append("Variables\n")
        for i in range(num_vars):
            lines.append(f"    x{i+1}\n")
        lines.append("    obj\n;\n\n")
        
        # Equation declarations
        lines.append("Equations\n")
        for j in range(num_constraints):
            lines.append(f"    c{j+1}\n")
        lines.append("    objdef\n;\n\n")
        
        # Equation definitions (simple quadratic constraints)
        for j in range(num_constraints):
            # Each constraint: sum of a few variables <= constant
            involved_vars = [f"x{(j*3+i) % num_vars + 1}" for i in range(min(3, num_vars))]
            lines.append(f"c{j+1}.. {' + '.join(involved_vars)} =L= {j+1};\n")
        
        lines.append("\n")
        
        # Objective (simple quadratic)
        obj_terms = [f"x{i+1}*x{i+1}" for i in range(num_vars)]
        lines.append(f"objdef.. obj =E= {' + '.join(obj_terms)};\n\n")
        
        # Model and solve
        lines.append("Model testModel /all/;\n")
        lines.append("Solve testModel using NLP minimizing obj;\n")
        
        model_file.write_text(''.join(lines))
        return model_file
```

### Acceptance Criteria

- [ ] Benchmark suite created with 6+ benchmarks
- [ ] Tests for small (10), medium (100), large (1000) variables
- [ ] Scalability tests verify sub-quadratic complexity
- [ ] Memory usage tests verify reasonable limits
- [ ] Sparsity exploitation verified
- [ ] Baselines documented for future comparison
- [ ] Added to CI (optional, may be slow)

### Expected Outcome

After Sprint 4 features added:
- Run benchmarks to verify performance
- Identify any regressions
- Document performance characteristics
- Set targets for Sprint 5 optimization

---

## Task 5: Improve Error Messages

**Priority:** Medium  
**Estimated Time:** 4 hours  
**Deadline:** Sprint 4 Day 5-6  
**Owner:** Development team

### Objective

Improve error messages to be user-friendly with actionable suggestions.

### Why This Matters

Sprint 3 Retrospective Action 2.3: "Error messages functional but not optimal. Some errors too technical for users."

Better error messages reduce support burden and improve user experience.

### Implementation Strategy

#### 1. Categorize All Errors

**User Errors** (bad input):
- Undefined variables/equations
- Syntax errors in GAMS
- Unsupported constructs
- Invalid bounds

**Internal Errors** (bugs):
- Assertion failures
- Missing attributes
- Inconsistent state

**System Errors** (environment):
- File not found
- GAMS not installed
- Permission errors

#### 2. Create Error Hierarchy

```python
# src/utils/errors.py

class NLP2MCPError(Exception):
    """Base exception for nlp2mcp."""
    pass

class UserError(NLP2MCPError):
    """Error caused by user input."""
    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format())
    
    def _format(self) -> str:
        msg = f"Error: {self.message}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        return msg

class InternalError(NLP2MCPError):
    """Internal nlp2mcp bug."""
    def __init__(self, message: str, context: dict = None):
        self.message = message
        self.context = context or {}
        super().__init__(self._format())
    
    def _format(self) -> str:
        msg = f"Internal Error: {self.message}\n"
        msg += "\nThis is a bug in nlp2mcp. Please report at:\n"
        msg += "https://github.com/user/nlp2mcp/issues\n"
        if self.context:
            msg += f"\nContext: {self.context}"
        return msg

class SystemError(NLP2MCPError):
    """System/environment error."""
    pass
```

#### 3. Replace Generic Exceptions

**Before:**
```python
raise ValueError(f"Variable {var} not found")
```

**After:**
```python
from src.utils.errors import UserError

available_vars = ', '.join(sorted(model.variables.keys()))
suggestion = f"Available variables: {available_vars}"

# Try fuzzy matching
similar = difflib.get_close_matches(var, model.variables.keys(), n=3)
if similar:
    suggestion += f"\n\nDid you mean: {', '.join(similar)}?"

raise UserError(
    f"Variable '{var}' not found in model",
    suggestion=suggestion
)
```

#### 4. Improve Parsing Errors

**Before:**
```
lark.exceptions.UnexpectedToken: Unexpected token Token('SEMICOLON', ';') at line 5
```

**After:**
```
Parse Error at line 5, column 12:
  x + y =e= 0;
           ^
Expected: equation name before '=e='

Suggestion: Did you forget to name the equation?
Try: myeq.. x + y =e= 0;
```

#### 5. Add Context to Internal Errors

```python
# When detecting inconsistency
if gradient.num_cols != jacobian.num_cols:
    raise InternalError(
        "Gradient and Jacobian have mismatched columns",
        context={
            'gradient_cols': gradient.num_cols,
            'jacobian_cols': jacobian.num_cols,
            'gradient_vars': list(gradient.mapping.instances),
            'jacobian_vars': list(jacobian.col_mapping.instances),
        }
    )
```

### Acceptance Criteria

- [ ] Error hierarchy created
- [ ] 20+ error sites improved with suggestions
- [ ] All user errors provide actionable suggestions
- [ ] All internal errors provide bug report link
- [ ] Parse errors show context and suggestions
- [ ] Tests verify error messages are helpful

### Expected Outcome

User encounters error:
```
Error: Variable 'cost' not found in model

Available variables: costs, demand, supply

Did you mean: costs?

Suggestion: Check variable spelling in your GAMS model.
Variables are case-sensitive.
```

Instead of:
```
KeyError: 'cost'
```

---

## Task 6: Create Edge Case Test Matrix

**Priority:** High  
**Estimated Time:** 3 hours  
**Deadline:** Sprint 4 Day 7-8  
**Owner:** Development team

### Objective

Create systematic test matrix for edge cases not covered in Sprint 3.

### Why This Matters

Sprint 3 Retrospective: "Day 10 edge case testing abbreviated. Many edge cases documented but not tested."

Need comprehensive edge case coverage before declaring production-ready.

### Deliverable

**File:** `docs/testing/EDGE_CASE_MATRIX.md`  
**Tests:** `tests/edge_cases/test_edge_cases.py`

### Edge Case Categories

#### 1. Constraint Types

| Case | Description | Expected Behavior | Test Status |
|------|-------------|-------------------|-------------|
| Only equalities | No inequalities, no bounds | KKT with only ν multipliers | ⏸️ Not tested |
| Only inequalities | No equalities | KKT with only λ multipliers | ⏸️ Not tested |
| Only bounds | No explicit constraints | KKT with only π multipliers | ⏸️ Not tested |
| Mixed all | Equalities + inequalities + bounds | Full KKT system | ✅ Golden tests |
| No constraints | Unconstrained optimization | KKT with only stationarity | ⏸️ Not tested |

#### 2. Bounds Configurations

| Case | Description | Expected Behavior | Test Status |
|------|-------------|-------------------|-------------|
| All finite | lo and up finite | Both πL and πU | ✅ Tested |
| All INF | No finite bounds | No π multipliers | ⏸️ Not tested |
| Mixed finite/INF | Some finite, some INF | Only π for finite | ✅ Tested |
| Fixed (x.fx) | lo = up | Equality constraint, no π | ⏸️ Not tested |
| Duplicate bounds | Variable bound = constraint | Exclude from inequalities | ✅ Tested (unit) |

#### 3. Indexing Complexity

| Case | Description | Expected Behavior | Test Status |
|------|-------------|-------------------|-------------|
| Scalar only | No indexed vars/equations | Simple KKT | ✅ Golden tests |
| Single index | x(i) | Indexed equations | ✅ Golden tests |
| Multi-index | x(i,j,k) | Multi-dim indexed | ⏸️ Not tested |
| Sparse indexing | x(i) only defined for i in subset | Partial indexing | ⏸️ Not tested |
| Aliased sets | i, ii as aliases | Handle correctly | ⏸️ Not tested |

#### 4. Expression Complexity

| Case | Description | Expected Behavior | Test Status |
|------|-------------|-------------------|-------------|
| Constants only | obj = 5; | Trivial gradient | ⏸️ Not tested |
| Linear | a*x + b*y | Simple derivatives | ✅ Tested |
| Quadratic | x^2 + y^2 | Power differentiation | ✅ Tested |
| Highly nonlinear | exp(x)*log(y)/sqrt(z) | Chain rule | ✅ Tested |
| Very long expr | 100+ terms | No stack overflow | ⏸️ Not tested |

#### 5. Sparsity Patterns

| Case | Description | Expected Behavior | Test Status |
|------|-------------|-------------------|-------------|
| Dense | All vars in all constraints | Large Jacobian | ⏸️ Not tested |
| Very sparse | Each constraint touches 1-2 vars | Efficient | ✅ Implicit |
| Block diagonal | Separable structure | Exploit structure | ⏸️ Not tested |
| Empty rows/cols | Some equations/vars disconnected | Warn or error | ⏸️ Not tested |

### Implementation Plan

For each edge case marked ⏸️:

1. **Create minimal test model**
2. **Define expected behavior**
3. **Implement test**
4. **Document if behavior surprising**

### Example Test

```python
# tests/edge_cases/test_edge_cases.py

def test_only_equalities_no_inequalities():
    """
    Edge case: Model with only equality constraints.
    
    Expected: KKT system has:
    - Stationarity equations (one per variable)
    - No λ multipliers (no inequalities)
    - No π multipliers (no bounds)
    - Only ν multipliers (for equalities)
    """
    model_gms = """
    Variables x, y, obj;
    Equations eq1, eq2, objdef;
    
    eq1.. x + y =e= 1;
    eq2.. x - y =e= 0;
    objdef.. obj =e= x^2 + y^2;
    
    Model test / all /;
    Solve test using NLP minimizing obj;
    """
    
    # Convert
    mcp = convert_to_mcp(model_gms)
    
    # Verify structure
    assert len(mcp.multipliers_eq) == 2  # nu_eq1, nu_eq2
    assert len(mcp.multipliers_ineq) == 0  # No λ
    assert len(mcp.multipliers_bounds_lo) == 0  # No πL
    assert len(mcp.multipliers_bounds_up) == 0  # No πU
    
    # Verify stationarity includes only ν terms
    stat_x = mcp.stationarity['x']
    # Should be: 2*x + ν_eq1 - ν_eq2 = 0
    # (No λ or π terms)
```

### Acceptance Criteria

- [ ] Edge case matrix document created with 25+ cases
- [ ] All cases categorized and prioritized
- [ ] High-priority cases have tests implemented
- [ ] Tests cover all categories
- [ ] Unexpected behaviors documented
- [ ] Matrix updated with test status

---

## Task 7: Formalize Checkpoint Templates

**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 4 Day 1  
**Owner:** Sprint planning

### Objective

Create formal checkpoint templates based on Sprint 3 experience.

### Why This Matters

Sprint 3 Retrospective Action 3.1: "Mid-sprint checkpoints were ad-hoc, not systematic."

Need structured checkpoints to catch issues early in Sprint 4.

### Deliverable

**File:** `docs/process/CHECKPOINT_TEMPLATES.md`

### Template Structure

```markdown
# Sprint 4 Checkpoint Templates

## Checkpoint 1: Day 3 (New Features Initial Implementation)

**When:** End of Day 3, before starting Day 4  
**Duration:** 30 minutes  
**Format:** Self-review with documented results

### Review Questions

1. **Feature Completeness**
   - [ ] Are all Day 1-3 features implemented?
   - [ ] Do smoke tests pass?
   - [ ] Are new features integrated with existing code?

2. **Known Unknowns Status**
   - [ ] Have all Day 1-3 unknowns been investigated?
   - [ ] Were any assumptions wrong? (Document)
   - [ ] Are new unknowns discovered? (Add to list)

3. **Test Coverage**
   - [ ] Do new features have unit tests?
   - [ ] Are integration tests added?
   - [ ] Current test count: _____ (target: 650+)

4. **Code Quality**
   - [ ] Does mypy pass with no errors?
   - [ ] Does ruff pass with no warnings?
   - [ ] Are docstrings complete?

### Artifacts to Review

- Test results: `pytest tests/ -v --tb=short`
- Known unknowns: `docs/planning/SPRINT_4/KNOWN_UNKNOWNS.md`
- Code coverage: `pytest --cov=src tests/`

### Acceptance Criteria

- ✅ All Day 1-3 tasks complete
- ✅ Smoke tests passing
- ✅ No unknown assumptions remaining
- ✅ Test coverage > 85%
- ✅ All code quality checks pass

### Decision Point

**If all criteria met:** ✅ Proceed to Day 4

**If any criteria fail:** ❌ STOP
- Document blockers
- Create recovery plan
- Re-run checkpoint when fixed

### Checkpoint Report

```
# Checkpoint 1 Report - Sprint 4 Day 3

Date: [Date]
Reviewer: [Name]

## Status: [PASS / FAIL]

## Review Results:
[Answer all questions above]

## Test Results:
[Paste test summary]

## Issues Found:
[List any problems]

## Action Items:
[If checkpoint fails]

## Decision:
[Proceed / Stop and fix]
```

[Similar templates for Checkpoints 2 (Day 6) and 3 (Day 8)]
```

### Acceptance Criteria

- [ ] 3 checkpoint templates created (Days 3, 6, 8)
- [ ] Each has clear review questions
- [ ] Each has acceptance criteria
- [ ] Each has decision point (go/no-go)
- [ ] Report template included
- [ ] Reminders set for checkpoint days

---

## Task 8: Review and Update Documentation

**Priority:** Medium  
**Estimated Time:** 3 hours  
**Deadline:** Sprint 4 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Issue #47 resolved)

### Objective

Update all documentation to reflect Issue #47 fix and Sprint 3 completion.

### Documents to Update

1. **KKT_ASSEMBLY.md**
   - Update stationarity section with indexed equations
   - Remove element-specific equation examples
   - Add Issue #47 lessons learned

2. **GAMS_EMISSION.md**
   - Verify all examples show indexed equations
   - Update Model MCP declaration syntax
   - Add section on index handling

3. **README.md**
   - Update Sprint 3 status: ✅ COMPLETE
   - Add Sprint 4 status: 🔄 IN PROGRESS
   - Update feature list with Sprint 4 planned features

4. **TESTING.md**
   - Add PATH solver validation section
   - Add edge case testing section
   - Update test pyramid

5. **CHANGELOG.md**
   - Add v0.1.1 section with Issue #47 fix
   - Document any breaking changes

### Acceptance Criteria

- [ ] All documents reviewed and updated
- [ ] Issue #47 lessons learned documented
- [ ] Sprint 4 plans documented
- [ ] Examples verified correct
- [ ] Changelog updated

---

## Task 9: Plan Sprint 4 Scope and Schedule

**Priority:** Critical  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 4 Day 1  
**Owner:** Sprint planning  
**Dependencies:** All prep tasks

### Objective

Create detailed Sprint 4 plan incorporating lessons learned from Sprint 3.

### Deliverable

**File:** `docs/planning/SPRINT_4/PLAN.md`

### Required Sections

1. **Sprint Goals** (from PROJECT_PLAN.md Sprint 4)
2. **Day-by-Day Plan** (Days 1-10)
3. **Integration Risks** (per day)
4. **Complexity Estimates** (per day)
5. **Known Unknowns Reference** (link to Task 2)
6. **Checkpoint Schedule** (Days 3, 6, 8)
7. **Acceptance Criteria**
8. **Contingency Plans**

### Sprint 4 Features (from PROJECT_PLAN.md)

**Priority 1 (Must Have):**
- `$include` support
- `min/max` reformulation with auxiliary variables
- `abs(x)` handling (reject or smooth)
- `x.fx` (fixed variables)

**Priority 2 (Should Have):**
- Parameter `Table` data blocks
- Scaling heuristics
- Model diagnostics

**Priority 3 (Nice to Have):**
- Advanced smoothing options
- Matrix Market Jacobian export

### Tentative Schedule

- **Days 1-2:** `$include` and parameter Table parsing
- **Day 3:** `min/max` reformulation (auxiliary variables)
- **Checkpoint 1**
- **Days 4-5:** `abs(x)` handling and `x.fx` support
- **Day 6:** Scaling implementation
- **Checkpoint 2**
- **Days 7-8:** Diagnostics and testing
- **Checkpoint 3**
- **Days 9-10:** Documentation and polish

### Lessons Applied from Sprint 3

1. **Known unknowns created proactively** (Task 2)
2. **Validation environment set up early** (Task 3)
3. **Performance baselines established** (Task 4)
4. **Checkpoints formalized** (Task 7)
5. **Edge cases planned** (Task 6)

### Acceptance Criteria

- [ ] Plan created with all required sections
- [ ] All days have integration risks documented
- [ ] All days have complexity estimates
- [ ] Checkpoint schedule defined
- [ ] Known unknowns list referenced
- [ ] Contingency plans for high-risk days
- [ ] Acceptance criteria clear
- [ ] Plan reviewed and approved

---

## Summary: Prep Task Execution Order

Execute in this logical order:

**Phase 1: Critical Fixes (Complete Before Sprint 4)**
1. ✅ Task 1: Resolve Issue #47 (COMPLETED post-Sprint 3)
2. Task 2: Create Known Unknowns List (2 hours)
3. Task 3: Set Up PATH Solver (4 hours)

**Phase 2: Quality Improvements (Can overlap)**
4. Task 4: Performance Benchmarking (4 hours)
5. Task 6: Edge Case Test Matrix (3 hours)
6. Task 7: Checkpoint Templates (2 hours)

**Phase 3: Documentation and Planning**
7. Task 8: Update Documentation (3 hours)
8. Task 5: Improve Error Messages (4 hours) [can be done during Sprint 4]
9. Task 9: Plan Sprint 4 Scope (4 hours)

**Total Time:** ~28 hours (~3.5 days)

**Critical Path:** 1 → 2 → 3 → 9 (~12 hours minimum)

---

## Prep Completion Checklist

Before Sprint 4 Day 1, verify:

### Critical (Must Complete)
- [x] Issue #47 resolved and verified (DONE)
- [ ] Known unknowns list created with 30+ items
- [ ] PATH solver installed and validated
- [ ] Sprint 4 plan created with integration risks

### High Priority (Should Complete)
- [ ] Performance benchmarks implemented
- [ ] Edge case matrix created
- [ ] Checkpoint templates formalized
- [ ] Documentation updated

### Medium Priority (Can Complete Early in Sprint 4)
- [ ] Error messages improved
- [ ] All edge cases tested

### Verification

```bash
# Verify Issue #47 fix
pytest tests/golden/ -v
# Should see: 5/5 passed

# Verify PATH solver setup
pytest tests/validation/test_path_solver.py -v
# Should see: tests run (or skipped if PATH unavailable)

# Verify test count
pytest --collect-only | grep "tests collected"
# Should see: 650+ tests collected

# Verify code quality
mypy src/
ruff check src/
# Should see: no errors
```

**When all critical items checked: Sprint 4 ready to begin.**

---

## Expected Benefits for Sprint 4

With prep tasks complete:

1. **No Issue #47-style emergencies:** Early validation catches syntax issues
2. **Clear unknowns:** All assumptions documented and verified
3. **Quality validated:** PATH solver confirms mathematical correctness
4. **Performance known:** Benchmarks establish baselines
5. **Systematic reviews:** Checkpoints prevent late issues
6. **Better errors:** Users get helpful messages

**Estimated time saved:** 2-3 days (avoiding Issue #47-style problems)  
**Prep investment:** 3.5 days  

**Net benefit:** Sprint 4 completes on time with higher quality

---

## Action Items from Sprint 3 Retrospective

This prep plan addresses these Sprint 3 action items:

### Priority 1 (Addressed)
- ✅ Action 1.1: Create Known Unknowns List BEFORE Sprint (Task 2)
- ✅ Action 1.2: Set Up Validation Environment on Day 0 (Task 3)
- ✅ Action 1.3: Test Code Generation Syntax Immediately (Task 3 + checklist)
- ✅ Action 1.4: Complete ALL PREP_PLAN Tasks Before Sprint (This plan!)

### Priority 2 (Addressed)
- ✅ Action 2.1: Add Performance Benchmarking (Task 4)
- ✅ Action 2.2: Set Up PATH Solver Validation (Task 3)
- ✅ Action 2.3: Improve Error Messages (Task 5)

### Priority 3 (Addressed)
- ✅ Action 3.1: Formalize Mid-Sprint Checkpoints (Task 7)
- ✅ Action 3.2: Write Design Docs Before Implementation (In Sprint 4 plan)
- ✅ Action 3.3: Daily Unknown Review (In Sprint 4 process)

### Future Sprints
- Action 4.1: Create Sprint Backlog (Sprint 4 planning)
- Action 4.2: Establish Definition of Done (Sprint 4 planning)
- Action 4.3: Complexity Estimation (Sprint 4 planning)

---

## Conclusion

This prep plan applies all lessons learned from Sprint 3 Retrospective to set up Sprint 4 for success. By completing these tasks before Sprint 4 begins, we prevent Issue #47-style emergencies and ensure systematic quality throughout the sprint.

**Key Success Factors:**
1. Proactive unknown documentation (not retrospective)
2. Early validation with actual tools (GAMS, PATH)
3. Systematic checkpoints (not ad-hoc)
4. Clear quality gates (performance, tests, coverage)

**Sprint 4 is ready to begin when all Critical items are checked off.**

---

**Document Created:** October 31, 2025  
**Sprint 4 Target Start:** TBD  
**Next Steps:** Execute prep tasks in order, verify completion, begin Sprint 4
