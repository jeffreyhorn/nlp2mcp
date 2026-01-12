# PATH Solver Integration Guide

**Purpose:** Document PATH solver availability, invocation, solution extraction, and error handling for Sprint 15 solve testing infrastructure.

**Created:** 2026-01-11  
**Status:** Validated and Ready for Sprint 15

---

## Executive Summary

PATH solver is available and properly configured for MCP solving. This guide documents:

1. **Environment:** GAMS 51.3.0 with PATH 5.2.01, demo license valid until Jan 23, 2026
2. **Invocation:** `gams model.gms` with `option mcp = path;`
3. **Solution Extraction:** Parse .lst files for SOLVER STATUS, MODEL STATUS, variable values
4. **Error Handling:** Status codes for optimal, infeasible, iteration/time limits, compilation errors
5. **Python Integration:** Existing patterns in `verify_convexity.py` and `test_path_solver.py`

**Key Finding:** Existing infrastructure in `scripts/gamslib/verify_convexity.py` provides robust .lst file parsing that can be reused for Sprint 15 solve testing.

---

## 1. Environment Setup

### 1.1 GAMS Installation

**Verified Configuration:**
```
GAMS Version: 51.3.0 (38407a9b, Oct 27, 2025)
Platform: macOS x86 64bit
Location: /Library/Frameworks/GAMS.framework/Versions/51/Resources/gams
```

**Verification Command:**
```bash
which gams
# Output: /Library/Frameworks/GAMS.framework/Versions/51/Resources/gams

gams 2>&1 | grep "GAMS Release"
# Output: *** GAMS Release     : 51.3.0 38407a9b DEX-DEG x86 64bit/macOS
```

### 1.2 PATH Solver Availability

**Verified Configuration:**
```
PATH Version: 5.2.01 (Mon Oct 27 13:31:58 2025)
Authors: Todd Munson, Steven Dirkse, Youngdae Kim, and Michael Ferris
Library: libpath52.dylib
```

**Verification:**
```bash
ls /Library/Frameworks/GAMS.framework/Versions/51/Resources/ | grep -i path
# Output:
# libpath52.dylib
# optpath.def
# optpathnlp.def
```

### 1.3 License Requirements

**Current License:**
- Type: GAMS Demo License
- Expiration: January 23, 2026
- Limitations: Demo license for demonstration and instructional purposes
- Location: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/gamslice.txt`

**License Check:**
```bash
gams 2>&1 | grep -E "License|Expiration"
# Output:
# *** License          : /Library/Frameworks/.../gamslice.txt
# *** Expiration date of time-limited license (GAMS base module) : Jan 23, 2026
```

**Demo License Limits:**
- The demo license may limit model size (variables, equations)
- PATH solver outputs: `*** This solver runs with a demo license. No commercial use.`
- For large models, a full license may be required

---

## 2. Invocation Approach

### 2.1 Basic MCP Solve Command

```bash
gams model_mcp.gms
```

**With Options:**
```bash
gams model_mcp.gms lo=3 o=output.lst
```

**Options:**
| Option | Description | Recommended |
|--------|-------------|-------------|
| `lo=3` | Log output level (3 = detailed) | Yes, for debugging |
| `o=file.lst` | Specify output .lst file location | Yes, for parsing |
| `reslim=N` | Time limit in seconds | Yes, 60-300s |
| `iterlim=N` | Iteration limit | Optional |

### 2.2 MCP Model Requirements

The generated MCP file must include:
```gams
option mcp = path;
solve model_name using mcp;
```

**Example MCP Structure:**
```gams
$title KKT Reformulation of NLP Model

* Variables
positive variables x1, x2;
variables lambda_eq1, mu_ineq1;

* KKT Equations
equations stat_x1, stat_x2, eq1, ineq1;

stat_x1.. <gradient of Lagrangian w.r.t. x1> =n= 0;
stat_x2.. <gradient of Lagrangian w.r.t. x2> =n= 0;
eq1..     <equality constraint> =n= 0;
ineq1..   <inequality constraint> =n= 0;

* MCP Model Definition (equation.variable pairs)
model mcp_model /stat_x1.x1, stat_x2.x2, eq1.lambda_eq1, ineq1.mu_ineq1/;

option mcp = path;
solve mcp_model using mcp;
```

### 2.3 Timeout Configuration

**Recommended Timeouts:**
| Model Size | Recommended Timeout |
|------------|---------------------|
| Small (< 100 vars) | 30 seconds |
| Medium (100-1000 vars) | 60 seconds |
| Large (> 1000 vars) | 300 seconds |

**Setting Timeout:**
```gams
option reslim = 60;  * 60 second time limit
```

Or via command line:
```bash
gams model.gms reslim=60
```

---

## 3. Solution Extraction

### 3.1 .lst File Structure

The GAMS .lst (listing) file contains solve results in a structured format:

```
S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  105

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

 RESOURCE USAGE, LIMIT          0.155 10000000000.000
 ITERATION COUNT, LIMIT        27    2147483647

---- VAR obj               -INF       -26272.5145        +INF             .
---- VAR x1                  .             0.6178        +INF      -3.37423E-10
---- VAR x2                  .             0.3282        +INF      -5.98448E-10
```

### 3.2 Status Code Extraction

**SOLVER STATUS Codes:**
| Code | Description | Sprint 15 Category |
|------|-------------|-------------------|
| 1 | Normal Completion | `path_solve_normal` |
| 2 | Iteration Interrupt | `path_solve_iteration_limit` |
| 3 | Resource Interrupt (time) | `path_solve_time_limit` |
| 4 | Terminated by Solver | `path_solve_terminated` |
| 5 | Evaluation Error Limit | `path_solve_eval_error` |
| 7 | Licensing Problem | `path_solve_license` |

**MODEL STATUS Codes:**
| Code | Description | Sprint 15 Category |
|------|-------------|-------------------|
| 1 | Optimal | `model_optimal` |
| 2 | Locally Optimal | `model_locally_optimal` |
| 4 | Infeasible | `model_infeasible` |
| 5 | Locally Infeasible | `model_infeasible` |
| 6 | Intermediate Infeasible | `model_infeasible` |

**Regex Patterns:**
```python
import re

# SOLVER STATUS extraction
solver_pattern = re.compile(r"\*\*\*\* SOLVER STATUS\s+(\d+)\s+(.*?)$", re.MULTILINE)

# MODEL STATUS extraction  
model_pattern = re.compile(r"\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)

# OBJECTIVE VALUE extraction (if present)
objective_pattern = re.compile(
    r"\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.MULTILINE,
)

# RESOURCE/ITERATION extraction
resource_pattern = re.compile(
    r"RESOURCE USAGE, LIMIT\s+([\d.]+)\s+([\d.]+)",
    re.MULTILINE,
)
iteration_pattern = re.compile(
    r"ITERATION COUNT, LIMIT\s+(\d+)\s+(\d+)",
    re.MULTILINE,
)
```

### 3.3 Variable Value Extraction

**Scalar Variable Pattern:**
```
---- VAR varname    LOWER     LEVEL     UPPER    MARGINAL
                    -INF      1.2345    +INF     0.0000
```

**Indexed Variable Pattern:**
```
---- VAR x  description

          LOWER     LEVEL     UPPER    MARGINAL

i1        -INF      1.0000    +INF       .
i2        -INF      2.0000    +INF       .
```

**Extraction Pattern:**
```python
# Scalar variable on same line as ---- VAR
SCALAR_VAR_PATTERN = r"---- VAR (\w+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)"

# Indexed variable in subsequent lines
INDEXED_VAR_PATTERN = r"(\w+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)"
```

### 3.4 Compilation Error Detection

**Patterns for Compilation Errors:**
```python
# Compilation error indicator
if re.search(r"\*\*\*\* \$\d+", lst_content):
    error_type = "compilation_error"

# Specific error codes
# $409 - Unrecognizable item
# $257 - Solve statement not checked due to previous errors

# Error count
error_match = re.search(r"\*\*\*\* (\d+) ERROR\(S\)", lst_content)
```

---

## 4. Error Handling

### 4.1 Error Scenarios Tested

| Scenario | SOLVER STATUS | MODEL STATUS | Detection |
|----------|---------------|--------------|-----------|
| Optimal solve | 1 | 1 | Success |
| Infeasible | 1 | 4 | `model_status == 4` |
| Iteration limit | 2 | 6 | `solver_status == 2` |
| Time limit | 3 | 6 | `solver_status == 3` |
| Compilation error | N/A | N/A | `**** $NNN` pattern |
| License limit | 7 | N/A | `solver_status == 7` or message |

### 4.2 Detection Patterns

```python
def categorize_solve_result(solver_status: int, model_status: int, lst_content: str) -> str:
    """Categorize MCP solve result.
    
    Returns one of the Sprint 15 solve outcome categories.
    """
    # Check for compilation errors first
    if re.search(r"\*\*\*\* \$\d+", lst_content):
        return "path_syntax_error"
    
    # Check for license limits
    if "exceeds the demo license limits" in lst_content:
        return "path_solve_license"
    
    # Check solver status
    if solver_status == 2:
        return "path_solve_iteration_limit"
    if solver_status == 3:
        return "path_solve_time_limit"
    if solver_status == 4:
        return "path_solve_terminated"
    if solver_status == 5:
        return "path_solve_eval_error"
    if solver_status == 7:
        return "path_solve_license"
    if solver_status != 1:
        return "compare_mcp_failed"
    
    # Solver completed normally, check model status
    if model_status == 1:
        return "model_optimal"
    if model_status == 2:
        return "model_locally_optimal"
    if model_status in (4, 5, 6):
        return "model_infeasible"
    
    return "compare_mcp_failed"
```

### 4.3 Error Messages from PATH

**Common PATH Exit Messages:**
```
** EXIT - solution found.           -> Success (model_status=1)
** EXIT - infeasible.               -> Infeasible (model_status=4)
** EXIT - iteration limit.          -> Iteration limit (solver_status=2)
** EXIT - time limit.               -> Time limit (solver_status=3)
```

---

## 5. Python Integration

### 5.1 Existing Code to Reuse

**Primary Source:** `scripts/gamslib/verify_convexity.py`
- `parse_gams_listing()` - Comprehensive .lst file parser
- `verify_model()` - Subprocess invocation with timeout
- Status code dictionaries for descriptions

**Additional Source:** `tests/validation/test_path_solver.py`
- `_solve_gams()` - MCP-specific solve wrapper
- `_extract_model_status()` / `_extract_solver_status()` - Simple extractors
- `_parse_gams_solution()` - Variable value extraction

### 5.2 Subprocess Invocation Example

```python
import subprocess
import tempfile
from pathlib import Path

def solve_mcp(mcp_file: Path, timeout_seconds: int = 60) -> dict:
    """Solve an MCP model using PATH solver.
    
    Args:
        mcp_file: Path to the .gms MCP file
        timeout_seconds: Maximum solve time
        
    Returns:
        dict with keys: success, solver_status, model_status, 
                       solve_time, iterations, error_category, error_message
    """
    mcp_file = Path(mcp_file).absolute()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        lst_path = Path(tmpdir) / "output.lst"
        
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                ["gams", str(mcp_file), f"o={lst_path}", "lo=3"],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=tmpdir,
            )
            
            solve_time = time.time() - start_time
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "solver_status": None,
                "model_status": None,
                "solve_time": timeout_seconds,
                "iterations": None,
                "error_category": "path_solve_time_limit",
                "error_message": f"Timeout after {timeout_seconds} seconds",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "solver_status": None,
                "model_status": None,
                "solve_time": 0,
                "iterations": None,
                "error_category": "path_solve_terminated",
                "error_message": "GAMS executable not found",
            }
        
        # Parse .lst file
        if not lst_path.exists():
            return {
                "success": False,
                "solver_status": None,
                "model_status": None,
                "solve_time": solve_time,
                "iterations": None,
                "error_category": "path_solve_terminated",
                "error_message": "No .lst file generated",
            }
        
        lst_content = lst_path.read_text()
        parsed = parse_solve_result(lst_content)
        parsed["solve_time"] = solve_time
        
        return parsed


def parse_solve_result(lst_content: str) -> dict:
    """Parse MCP solve result from .lst file content.
    
    Returns:
        dict with solver_status, model_status, iterations, success, 
             error_category, error_message
    """
    import re
    
    result = {
        "success": False,
        "solver_status": None,
        "model_status": None,
        "iterations": None,
        "error_category": None,
        "error_message": None,
    }
    
    # Check for compilation errors
    if re.search(r"\*\*\*\* \$\d+", lst_content):
        result["error_category"] = "path_syntax_error"
        result["error_message"] = "GAMS compilation error"
        return result
    
    # Check for license limits
    if "exceeds the demo license limits" in lst_content:
        result["error_category"] = "path_solve_license"
        result["error_message"] = "Model exceeds demo license limits"
        return result
    
    # Extract solver status
    solver_match = re.search(
        r"\*\*\*\* SOLVER STATUS\s+(\d+)", lst_content
    )
    if solver_match:
        result["solver_status"] = int(solver_match.group(1))
    
    # Extract model status
    model_match = re.search(
        r"\*\*\*\* MODEL STATUS\s+(\d+)", lst_content
    )
    if model_match:
        result["model_status"] = int(model_match.group(1))
    
    # Extract iterations
    iter_match = re.search(
        r"ITERATION COUNT, LIMIT\s+(\d+)", lst_content
    )
    if iter_match:
        result["iterations"] = int(iter_match.group(1))
    
    # Categorize result
    solver_status = result["solver_status"]
    model_status = result["model_status"]
    
    if solver_status == 1 and model_status in (1, 2):
        result["success"] = True
        result["error_category"] = "model_optimal" if model_status == 1 else "model_locally_optimal"
    elif solver_status == 2:
        result["error_category"] = "path_solve_iteration_limit"
        result["error_message"] = "Iteration limit reached"
    elif solver_status == 3:
        result["error_category"] = "path_solve_time_limit"
        result["error_message"] = "Time limit reached"
    elif model_status == 4:
        result["error_category"] = "model_infeasible"
        result["error_message"] = "Model is infeasible"
    else:
        result["error_category"] = "compare_mcp_failed"
        result["error_message"] = f"Solve failed: solver={solver_status}, model={model_status}"
    
    return result
```

### 5.3 Variable Extraction Example

```python
def extract_variable_values(lst_content: str) -> dict[str, float]:
    """Extract variable solution values from .lst file.
    
    Args:
        lst_content: Content of GAMS .lst file
        
    Returns:
        Dictionary mapping variable names to their LEVEL values
    """
    import re
    
    solution = {}
    
    # Find all ---- VAR sections
    var_sections = re.finditer(
        r"---- VAR (\w+)(.*?)(?=---- VAR|---- EQU|\*\*\*\*|$)",
        lst_content,
        re.DOTALL
    )
    
    for match in var_sections:
        var_name = match.group(1)
        section = match.group(2)
        
        # Try to extract scalar value (on same line or next line)
        # Format: LOWER LEVEL UPPER MARGINAL
        value_pattern = r"([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)"
        value_match = re.search(value_pattern, section)
        
        if value_match:
            level_str = value_match.group(2)
            try:
                if level_str in ('.', 'EPS'):
                    solution[var_name] = 0.0
                elif level_str in ('-INF', '+INF', 'INF'):
                    solution[var_name] = float('inf') if '+' in level_str or level_str == 'INF' else float('-inf')
                else:
                    solution[var_name] = float(level_str)
            except ValueError:
                pass
    
    return solution
```

---

## 6. Sprint 15 Recommendations

### 6.1 Recommended Approach

1. **Reuse existing infrastructure** from `verify_convexity.py`:
   - Use `parse_gams_listing()` for .lst file parsing
   - Use subprocess invocation pattern with timeout
   - Use status code dictionaries for descriptions

2. **Add MCP-specific handling**:
   - No OBJECTIVE VALUE in MCP solve summary (extract from variables)
   - Map solver/model status to Sprint 15 error taxonomy categories
   - Handle PATH-specific exit messages

3. **Default timeout:** 60 seconds (matches verify_convexity.py)

4. **Error handling priority:**
   1. Check for compilation errors first
   2. Check for license limits
   3. Check solver status (non-1 = failure)
   4. Check model status (1-2 = success, 4+ = failure)

### 6.2 Implementation Checklist

- [ ] Create `solve_mcp()` function in new or existing module
- [ ] Reuse `parse_gams_listing()` from verify_convexity.py
- [ ] Add MCP-specific status mapping to error taxonomy
- [ ] Implement objective value extraction from MCP solution
- [ ] Add solution comparison logic (NLP vs MCP objectives)
- [ ] Create database update function for solve results

### 6.3 Testing Strategy

1. **Unit tests:** Mock .lst file content, test parsing
2. **Integration tests:** Solve actual MCP files from data/gamslib/mcp/
3. **Error scenarios:** Test infeasible, iteration limit, time limit, syntax error
4. **Skip in CI:** Use `pytest.mark.skipif` when GAMS not available

---

## Appendix A: Status Code Reference

### GAMS Solver Status Codes
| Code | Name | Description |
|------|------|-------------|
| 1 | Normal Completion | Solver terminated normally |
| 2 | Iteration Interrupt | Iteration limit reached |
| 3 | Resource Interrupt | Time limit reached |
| 4 | Terminated by Solver | Solver terminated for other reason |
| 5 | Evaluation Error Limit | Too many evaluation errors |
| 6 | Capability Problem | Solver cannot handle model type |
| 7 | Licensing Problem | License issue |
| 8 | User Interrupt | User interrupted |
| 9 | Error Setup Failure | Setup failed |
| 10 | Error Solver Failure | Solver internal error |
| 11 | Error Internal Solver Error | Internal error |
| 12 | Solve Processing Skipped | Skipped |
| 13 | Error System Failure | System error |

### GAMS Model Status Codes
| Code | Name | Description |
|------|------|-------------|
| 1 | Optimal | Optimal solution found |
| 2 | Locally Optimal | Local optimum (NLP) |
| 3 | Unbounded | Model is unbounded |
| 4 | Infeasible | Model is infeasible |
| 5 | Locally Infeasible | Locally infeasible |
| 6 | Intermediate Infeasible | Infeasible intermediate point |
| 7 | Intermediate Non-Optimal | Non-optimal intermediate |
| 8 | Integer Solution | Integer solution found |
| 9 | Intermediate Non-Integer | Non-integer intermediate |
| 10 | Integer Infeasible | Integer infeasible |
| 11 | Licensing Problem | License issue |
| 12 | Error Unknown | Unknown error |
| 13 | Error No Solution | No solution found |
| 14 | No Solution Returned | Solver returned no solution |
| 15 | Solved Unique | Unique solution |
| 16 | Solved | Solved |
| 17 | Solved Singular | Singular solution |
| 18 | Unbounded - No Solution | Unbounded, no solution |
| 19 | Infeasible - No Solution | Infeasible, no solution |

---

## Appendix B: Test Results Summary

**Test Date:** 2026-01-11

| Test Case | SOLVER STATUS | MODEL STATUS | Result |
|-----------|---------------|--------------|--------|
| Simple MCP (test_path_mcp.gms) | 1 | 1 | Success |
| Generated MCP (hs62_mcp.gms) | 1 | 1 | Success |
| Infeasible MCP | 1 | 4 | Correctly detected |
| Iteration limit (iterlim=1) | 2 | 6 | Correctly detected |
| Time limit (reslim=0.001) | 3 | 6 | Correctly detected |
| Syntax error (missing semicolon) | N/A | N/A | Compilation error detected |

**Conclusion:** PATH solver integration is validated and ready for Sprint 15.
