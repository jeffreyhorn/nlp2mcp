# GAMS Environment Status for Sprint 13

**Date:** December 29, 2025  
**Sprint 13 Prep Task 3:** Validate GAMS Local Environment  
**Purpose:** Document GAMS environment and .lst file parsing patterns for convexity verification

---

## Executive Summary

GAMS environment is fully validated and ready for Sprint 13 convexity verification work.

**Key Findings:**
- GAMS 51.3.0 installed and accessible at `/Library/Frameworks/GAMS.framework/Versions/51/Resources/`
- Multiple NLP solvers available: CONOPT, IPOPT, MINOS, SNOPT, KNITRO
- Non-interactive batch mode works with predictable exit codes
- .lst file parsing patterns documented for status extraction
- Demo license sufficient for GAMSLIB model testing

---

## 1. GAMS Installation

### Version Information
```
GAMS Release     : 51.3.0 38407a9b DEX-DEG x86 64bit/macOS
Release Date     : Oct 27, 2025
System Directory : /Library/Frameworks/GAMS.framework/Versions/51/Resources/
License          : GAMS Demo (G250826+0003Cc-GEN)
```

### Accessibility
```bash
$ which gams
/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams

$ gamslib
# Available - can extract GAMSLIB models
```

**Status:** GAMS is on PATH and accessible from any directory.

---

## 2. Available Solvers

### NLP Solvers
| Solver | Library | Status | Notes |
|--------|---------|--------|-------|
| CONOPT | libconopt464.dylib | Available | Default NLP solver |
| IPOPT | libipopt.dylib | Available | Interior point |
| MINOS | optminos.def | Available | SQP-based |
| SNOPT | optsnopt.def | Available | SQP-based |
| KNITRO | libknitro1501.dylib | Available | Commercial |

### LP/MIP Solvers
| Solver | Status | Notes |
|--------|--------|-------|
| CPLEX | Available | Default LP solver |

### MCP Solver
| Solver | Library | Status | Notes |
|--------|---------|--------|-------|
| PATH | libpath52.dylib | Available | For complementarity problems |

---

## 3. Non-Interactive Batch Mode

### Command Syntax
```bash
gams model.gms [options]
```

### Key Options
| Option | Description | Example |
|--------|-------------|---------|
| `lo=N` | Log output level (0-4) | `lo=3` for summary only |
| `o=file` | Output file path | `o=/tmp/model.lst` |
| `NLP=solver` | Set NLP solver | `NLP=IPOPT` |
| `LP=solver` | Set LP solver | `LP=CPLEX` |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Normal completion (may include solve issues) |
| 2 | Compilation error |
| Other | Various runtime errors |

**Note:** Exit code 0 does not guarantee optimal solution - must check MODEL STATUS in .lst file.

---

## 4. .lst File Parsing Patterns

### Key Status Lines

The solve summary section contains critical status information:

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE                0.5000
```

### Regex Patterns for Parsing

```python
import re

# Solver status
solver_status_pattern = r'\*\*\*\* SOLVER STATUS\s+(\d+)\s+(.*)'
# Match: "**** SOLVER STATUS     1 Normal Completion"
# Groups: (1, "Normal Completion")

# Model status
model_status_pattern = r'\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*)'
# Match: "**** MODEL STATUS      2 Locally Optimal"
# Groups: (2, "Locally Optimal")

# Objective value
objective_pattern = r'\*\*\*\* OBJECTIVE VALUE\s+([\d.E+-]+)'
# Match: "**** OBJECTIVE VALUE                0.5000"
# Groups: ("0.5000",)
```

### SOLVER STATUS Codes

| Code | Name | Description |
|------|------|-------------|
| 1 | Normal Completion | Solver terminated normally |
| 2 | Iteration Limit | Maximum iterations reached |
| 3 | Resource Limit | Time or memory limit |
| 4 | Terminated by Solver | Internal solver termination |
| 5 | Evaluation Error | Error evaluating functions |
| 6 | Capability Problem | Solver cannot handle model |
| 7 | Licensing Problem | License issue |
| 8 | User Interrupt | Ctrl+C or similar |
| 9 | Setup Failure | Solver initialization failed |
| 10 | Solver Failure | Internal solver error |
| 11 | Internal Solver Error | Bug in solver |
| 12 | Solve Processing Skipped | Solve not attempted |
| 13 | System Failure | System-level failure |

### MODEL STATUS Codes

| Code | Name | Convexity Implication |
|------|------|----------------------|
| 1 | Optimal | **Convex** - Global optimum found |
| 2 | Locally Optimal | **Unknown** - Local solver found local optimum |
| 3 | Unbounded | Exclude from corpus |
| 4 | Infeasible | Exclude from corpus |
| 5 | Locally Infeasible | Exclude from corpus |
| 6 | Intermediate Infeasible | Exclude from corpus |
| 7 | Intermediate Nonoptimal | Retry or exclude |
| 8 | Integer Solution | N/A (integer models excluded) |
| 9 | Intermediate Non-Integer | N/A |
| 10 | Integer Infeasible | N/A |
| 11 | Licensing Problem | Error - exclude |
| 12 | Error Unknown | Error - exclude |
| 13 | Error No Solution | Error - exclude |
| 14 | No Solution Returned | Error - exclude |
| 15 | Solved Unique | Optimal (for CNS) |
| 16 | Solved | Optimal (for CNS) |
| 17 | Solved Singular | Caution |
| 18 | Unbounded - No Solution | Exclude |
| 19 | Infeasible - No Solution | Exclude |

### Convexity Classification Logic

```python
def classify_convexity(model_type: str, model_status: int) -> str:
    """
    Classify model convexity based on type and solve status.
    
    Returns: 'convex', 'non_convex', 'unknown', or 'excluded'
    """
    if model_type == 'LP':
        # LP is always convex by definition
        if model_status == 1:
            return 'convex'
        elif model_status in (3, 4, 5, 6):
            return 'excluded'  # Unbounded/infeasible
        else:
            return 'unknown'
    
    elif model_type == 'NLP':
        if model_status == 1:
            return 'convex'  # Solver found global optimum
        elif model_status == 2:
            return 'unknown'  # Local solver, can't verify convexity
        elif model_status in (3, 4, 5, 6):
            return 'excluded'  # Unbounded/infeasible
        else:
            return 'unknown'
    
    else:
        return 'excluded'  # Other model types excluded
```

---

## 5. Test Results

### Convex NLP (MODEL STATUS = 2)
```gams
* min x^2 + y^2 s.t. x + y >= 1
Solve test using NLP minimizing obj;
```
Result: `MODEL STATUS = 2 (Locally Optimal)` with CONOPT

**Note:** Even convex problems may return STATUS 2 because local NLP solvers don't prove global optimality.

### LP (MODEL STATUS = 1)
```gams
* min -x - y s.t. x + y <= 10
Solve test using LP minimizing obj;
```
Result: `MODEL STATUS = 1 (Optimal)` with CPLEX

**Key Insight:** LP always returns STATUS 1 (Optimal) because LP solvers find global optimum.

### Infeasible Model (MODEL STATUS = 4)
```gams
* x + y >= 5 AND x + y <= 1
Solve test using NLP minimizing obj;
```
Result: `MODEL STATUS = 4 (Infeasible)`

### IPOPT Solver (MODEL STATUS = 2)
```gams
Option NLP = IPOPT;
* Same convex problem
```
Result: `MODEL STATUS = 2 (Locally Optimal)` - same as CONOPT

### Syntax Error (Exit Code = 2)
```gams
x.lo = -10 x.up = 10;  * Missing semicolon
```
Result: Exit code 2, error in .lst file

---

## 6. Recommendations for Sprint 13

### Convexity Verification Strategy

1. **LP Models:** Classify as `verified_convex` if MODEL STATUS = 1
2. **NLP Models:** 
   - MODEL STATUS = 1 → `verified_convex` (rare with local solvers)
   - MODEL STATUS = 2 → `locally_optimal` (cannot verify convexity with local solver)
   - Consider using global solver (BARON) if available
3. **Exclude:** MODEL STATUS in {3, 4, 5, 6, 11, 12, 13, 14, 18, 19}

### Parsing Implementation

```python
def parse_gams_listing(lst_content: str) -> dict:
    """Parse GAMS .lst file for solve status."""
    result = {
        'solver_status': None,
        'solver_status_text': None,
        'model_status': None,
        'model_status_text': None,
        'objective_value': None,
    }
    
    for line in lst_content.split('\n'):
        if '**** SOLVER STATUS' in line:
            match = re.search(r'(\d+)\s+(.*)', line)
            if match:
                result['solver_status'] = int(match.group(1))
                result['solver_status_text'] = match.group(2).strip()
        
        elif '**** MODEL STATUS' in line:
            match = re.search(r'(\d+)\s*(.*)', line)
            if match:
                result['model_status'] = int(match.group(1))
                result['model_status_text'] = match.group(2).strip()
        
        elif '**** OBJECTIVE VALUE' in line:
            match = re.search(r'([\d.E+-]+)', line)
            if match:
                result['objective_value'] = float(match.group(1))
    
    return result
```

### Batch Execution

```bash
# Run model non-interactively
gams model.gms lo=3 o=model.lst
exit_code=$?

# Check exit code first
if [ $exit_code -ne 0 ]; then
    echo "GAMS error (exit code $exit_code)"
fi

# Parse .lst file for status
grep -E "SOLVER STATUS|MODEL STATUS|OBJECTIVE VALUE" model.lst
```

---

## 7. Demo License Considerations

### Limitations
- "Demo license for demonstration and instructional purposes only"
- No commercial use
- Size limits may apply for very large models

### Sufficient For
- GAMSLIB model testing (most models are small)
- Convexity verification pipeline
- Sprint 13 scope

---

## References

- GAMS Documentation: https://www.gams.com/latest/docs/
- Solver Status Codes: https://www.gams.com/latest/docs/UG_SolverUsage.html
- Model Status Codes: https://www.gams.com/latest/docs/UG_ModelSolveStatement.html
- PATH_SOLVER_STATUS.md: Previous Sprint 5 environment documentation

---

**Task 3 Status:** COMPLETE  
**Validation Date:** December 29, 2025
