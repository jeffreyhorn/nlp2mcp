# Convexity Verification Design for Sprint 13

**Date:** December 30, 2025  
**Sprint 13 Prep Task 5:** Research Convexity Verification Approaches  
**Purpose:** Design algorithm for verifying model convexity using GAMS solver output  
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7

---

## Executive Summary

This document defines the convexity verification approach for Sprint 13 GAMSLIB validation. The strategy uses GAMS solver output (MODEL STATUS and SOLVER STATUS) to classify models as convex, non-convex, or unknown.

**Key Decisions:**
- **LP models:** Always convex by definition
- **NLP/QCP models:** Verify via solver status codes
- **Primary solver:** CONOPT (default, local solver)
- **Timeout:** 60 seconds per model
- **Classification:** Conservative approach - only mark as convex when certain

---

## 1. GAMS Status Codes Reference

### 1.1 MODEL STATUS Codes

| Code | Name | Description | Convexity Implication |
|------|------|-------------|----------------------|
| 1 | Optimal | Global optimum found | Convex (LP only) |
| 2 | Locally Optimal | Local optimum found | Unknown (local solver) |
| 3 | Unbounded | Objective unbounded | Exclude |
| 4 | Infeasible | No feasible solution | Exclude |
| 5 | Locally Infeasible | Locally infeasible | Exclude |
| 6 | Intermediate Infeasible | Solver stopped, infeasible | Exclude |
| 7 | Intermediate Nonoptimal | Solver stopped, not optimal | Unknown |
| 8 | Integer Solution | Integer optimal | N/A (excluded type) |
| 9 | Intermediate Non-Integer | MIP not converged | N/A (excluded type) |
| 10 | Integer Infeasible | MIP infeasible | N/A (excluded type) |
| 11 | Licensing Problem | License issue | Error |
| 12 | Error Unknown | Unknown error | Error |
| 13 | Error No Solution | Error, no solution | Error |
| 14 | No Solution Returned | Solver returned nothing | Error |
| 15 | Solved Unique | Unique solution (CNS) | N/A (excluded type) |
| 16 | Solved | Solution found (CNS) | N/A (excluded type) |
| 17 | Solved Singular | Singular solution | Error |
| 18 | Unbounded - No Solution | Unbounded, no point | Exclude |
| 19 | Infeasible - No Solution | Infeasible, no point | Exclude |

### 1.2 SOLVER STATUS Codes

| Code | Name | Description |
|------|------|-------------|
| 1 | Normal Completion | Solver terminated normally |
| 2 | Iteration Limit | Max iterations reached |
| 3 | Resource Limit | Time/memory limit |
| 4 | Terminated by Solver | Internal termination |
| 5 | Evaluation Error | Function evaluation failed |
| 6 | Capability Problem | Solver can't handle model |
| 7 | Licensing Problem | License issue |
| 8 | User Interrupt | User stopped execution |
| 9 | Setup Failure | Initialization failed |
| 10 | Solver Failure | Internal solver error |
| 11 | Internal Solver Error | Solver bug |
| 12 | Solve Processing Skipped | Solve not attempted |
| 13 | System Failure | System-level failure |

### 1.3 Status Interpretation

**Valid solve:** SOLVER STATUS = 1 (Normal Completion)  
**Valid result:** MODEL STATUS in {1, 2} (Optimal or Locally Optimal)  
**Exclude:** MODEL STATUS in {3, 4, 5, 6, 18, 19} (Unbounded/Infeasible)  
**Error:** SOLVER STATUS != 1 or MODEL STATUS in {11, 12, 13, 14, 17}

---

## 2. Solver Selection

### 2.1 Available NLP Solvers

| Solver | Type | Global? | Demo License? | Recommended? |
|--------|------|---------|---------------|--------------|
| CONOPT | Interior Point | No | Yes | **Primary** |
| IPOPT | Interior Point | No | Yes | Secondary |
| MINOS | SQP | No | Yes | Alternative |
| SNOPT | SQP | No | Yes | Alternative |
| BARON | Branch & Bound | **Yes** | Limited | If available |
| ANTIGONE | MINLP | Yes | No | Not recommended |

### 2.2 Solver Recommendation

**Primary Solver: CONOPT**
- Default NLP solver in GAMS
- Robust and well-tested
- Available under demo license
- Fast for small/medium models
- Produces consistent status codes

**Secondary Solver: IPOPT**
- Use if CONOPT fails or times out
- Different algorithm may find solution

**Global Solver Consideration:**
- BARON provides global optimization guarantees
- If MODEL STATUS = 1 with BARON → definitely convex
- Demo license may limit BARON to small problems
- Consider for Sprint 14+ enhancement

### 2.3 Solver Selection Logic

```python
def select_solver(model_type: str, model_size: dict) -> str:
    """
    Select appropriate solver for convexity verification.
    
    Args:
        model_type: 'LP', 'NLP', or 'QCP'
        model_size: {'variables': int, 'equations': int}
    
    Returns:
        Solver name to use
    """
    if model_type == 'LP':
        return 'CPLEX'  # LP solver for linear programs
    
    # For NLP/QCP, use CONOPT as primary
    # Could add logic for BARON if available and model is small
    return 'CONOPT'
```

---

## 3. Verification Algorithm

### 3.1 Classification Categories

| Category | Description | Criteria |
|----------|-------------|----------|
| `verified_convex` | Proven convex | LP with STATUS 1, or global solver with STATUS 1 |
| `likely_convex` | Probably convex | NLP with STATUS 2, no non-convex indicators |
| `unknown` | Cannot determine | NLP with STATUS 2, has non-convex indicators |
| `non_convex` | Known non-convex | Contains DNLP functions, bilinear terms |
| `excluded` | Not in corpus | Infeasible, unbounded, or wrong type |
| `error` | Solve failed | Solver error, timeout, or license issue |

### 3.2 Decision Tree

```
START
  │
  ├─ Model Type?
  │    │
  │    ├─ LP ────────────────────────────────────────────┐
  │    │                                                 │
  │    ├─ NLP/QCP ──────────────────────────────────────┐│
  │    │                                                ││
  │    └─ Other (MIP, MINLP, etc.) ──► EXCLUDED         ││
  │                                                     ││
  │   ┌─────────────────────────────────────────────────┘│
  │   │                                                  │
  │   ▼                                                  │
  │  Run GAMS with CONOPT                               │
  │   │                                                  │
  │   ├─ SOLVER STATUS != 1 ──► ERROR (timeout/failure) │
  │   │                                                  │
  │   └─ SOLVER STATUS = 1                              │
  │        │                                             │
  │        ├─ MODEL STATUS = 1 ──► LIKELY_CONVEX        │
  │        │   (local solver can't prove global)        │
  │        │                                             │
  │        ├─ MODEL STATUS = 2 ──► LIKELY_CONVEX        │
  │        │   (same for local solver)                  │
  │        │                                             │
  │        ├─ MODEL STATUS in {3,4,5,6,18,19}           │
  │        │   ──► EXCLUDED (unbounded/infeasible)      │
  │        │                                             │
  │        └─ MODEL STATUS in {11,12,13,14,17}          │
  │            ──► ERROR                                │
  │                                                      │
  ├──────────────────────────────────────────────────────┘
  │
  ▼
 LP Path:
  Run GAMS with CPLEX
   │
   ├─ MODEL STATUS = 1 ──► VERIFIED_CONVEX
   │   (LP solver proves global optimality)
   │
   ├─ MODEL STATUS in {3,4,5,6,18,19}
   │   ──► EXCLUDED (unbounded/infeasible)
   │
   └─ Other ──► ERROR
```

### 3.3 Implementation

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ConvexityStatus(Enum):
    VERIFIED_CONVEX = "verified_convex"  # Proven convex (LP or global solver)
    LIKELY_CONVEX = "likely_convex"      # NLP solved, probably convex
    UNKNOWN = "unknown"                   # Cannot determine
    NON_CONVEX = "non_convex"            # Known non-convex
    EXCLUDED = "excluded"                 # Not in corpus
    ERROR = "error"                       # Solve failed

@dataclass
class VerificationResult:
    status: ConvexityStatus
    model_status: Optional[int]
    solver_status: Optional[int]
    objective_value: Optional[float]
    solve_time_seconds: float
    message: str

def verify_convexity(
    model_path: str,
    model_type: str,
    timeout_seconds: int = 60
) -> VerificationResult:
    """
    Verify convexity of a GAMS model by solving it.
    
    Args:
        model_path: Path to .gms file
        model_type: 'LP', 'NLP', or 'QCP'
        timeout_seconds: Maximum solve time
    
    Returns:
        VerificationResult with status and details
    """
    import subprocess
    import time
    import tempfile
    import os
    
    # Skip non-candidate types
    if model_type not in ('LP', 'NLP', 'QCP'):
        return VerificationResult(
            status=ConvexityStatus.EXCLUDED,
            model_status=None,
            solver_status=None,
            objective_value=None,
            solve_time_seconds=0.0,
            message=f"Model type {model_type} excluded from corpus"
        )
    
    # Create temp directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        lst_path = os.path.join(tmpdir, 'output.lst')
        
        # Select solver based on model type
        solver_option = 'LP=CPLEX' if model_type == 'LP' else 'NLP=CONOPT'
        
        # Run GAMS
        start_time = time.time()
        try:
            result = subprocess.run(
                ['gams', model_path, f'o={lst_path}', 'lo=3', solver_option],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=tmpdir
            )
            solve_time = time.time() - start_time
        except subprocess.TimeoutExpired:
            return VerificationResult(
                status=ConvexityStatus.ERROR,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=timeout_seconds,
                message=f"Timeout after {timeout_seconds} seconds"
            )
        
        # Check for compilation errors
        if result.returncode == 2:
            return VerificationResult(
                status=ConvexityStatus.ERROR,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                message="GAMS compilation error"
            )
        
        # Parse .lst file
        if not os.path.exists(lst_path):
            return VerificationResult(
                status=ConvexityStatus.ERROR,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                message="No listing file generated"
            )
        
        with open(lst_path, 'r') as f:
            lst_content = f.read()
        
        parsed = parse_gams_listing(lst_content)
        
        # Classify based on status codes
        return classify_result(
            model_type=model_type,
            solver_status=parsed['solver_status'],
            model_status=parsed['model_status'],
            objective_value=parsed['objective_value'],
            solve_time=solve_time
        )

def classify_result(
    model_type: str,
    solver_status: Optional[int],
    model_status: Optional[int],
    objective_value: Optional[float],
    solve_time: float
) -> VerificationResult:
    """Classify verification result based on status codes."""
    
    # Check for solver failure
    if solver_status is None or solver_status != 1:
        return VerificationResult(
            status=ConvexityStatus.ERROR,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message=f"Solver did not complete normally (status={solver_status})"
        )
    
    # Check for no model status
    if model_status is None:
        return VerificationResult(
            status=ConvexityStatus.ERROR,
            model_status=None,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message="No model status found in output"
        )
    
    # Exclude unbounded/infeasible
    if model_status in (3, 4, 5, 6, 18, 19):
        status_names = {
            3: 'Unbounded', 4: 'Infeasible', 5: 'Locally Infeasible',
            6: 'Intermediate Infeasible', 18: 'Unbounded - No Solution',
            19: 'Infeasible - No Solution'
        }
        return VerificationResult(
            status=ConvexityStatus.EXCLUDED,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message=f"Model is {status_names.get(model_status, 'excluded')}"
        )
    
    # Error status codes
    if model_status in (11, 12, 13, 14, 17):
        return VerificationResult(
            status=ConvexityStatus.ERROR,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message=f"Solver error (model status={model_status})"
        )
    
    # LP with optimal status
    if model_type == 'LP' and model_status == 1:
        return VerificationResult(
            status=ConvexityStatus.VERIFIED_CONVEX,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message="LP solver found global optimum"
        )
    
    # NLP/QCP with status 1 or 2 (local solver)
    if model_type in ('NLP', 'QCP') and model_status in (1, 2):
        return VerificationResult(
            status=ConvexityStatus.LIKELY_CONVEX,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            message="Local solver found optimum (convexity not proven)"
        )
    
    # Default to unknown
    return VerificationResult(
        status=ConvexityStatus.UNKNOWN,
        model_status=model_status,
        solver_status=solver_status,
        objective_value=objective_value,
        solve_time_seconds=solve_time,
        message=f"Unexpected status combination"
    )
```

---

## 4. .lst File Parsing

### 4.1 Parsing Patterns

```python
import re
from typing import Optional

def parse_gams_listing(lst_content: str) -> dict:
    """
    Parse GAMS .lst file for solve status.
    
    Returns:
        dict with keys: solver_status, solver_status_text,
                       model_status, model_status_text, objective_value
    """
    result = {
        'solver_status': None,
        'solver_status_text': None,
        'model_status': None,
        'model_status_text': None,
        'objective_value': None,
    }
    
    # Patterns
    solver_pattern = re.compile(
        r'\*\*\*\* SOLVER STATUS\s+(\d+)\s+(.*?)$',
        re.MULTILINE
    )
    model_pattern = re.compile(
        r'\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$',
        re.MULTILINE
    )
    objective_pattern = re.compile(
        r'\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)',
        re.MULTILINE
    )
    
    # Find last occurrence of each (handles multiple solves)
    solver_matches = list(solver_pattern.finditer(lst_content))
    if solver_matches:
        match = solver_matches[-1]
        result['solver_status'] = int(match.group(1))
        result['solver_status_text'] = match.group(2).strip()
    
    model_matches = list(model_pattern.finditer(lst_content))
    if model_matches:
        match = model_matches[-1]
        result['model_status'] = int(match.group(1))
        result['model_status_text'] = match.group(2).strip()
    
    objective_matches = list(objective_pattern.finditer(lst_content))
    if objective_matches:
        match = objective_matches[-1]
        result['objective_value'] = float(match.group(1))
    
    return result
```

### 4.2 Example .lst Content

```
                           S O L V E      S U M M A R Y

     MODEL   test                OBJECTIVE  obj
     TYPE    NLP                 DIRECTION  MINIMIZE
     SOLVER  CONOPT              FROM LINE  12

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE                0.5000

 RESOURCE USAGE, LIMIT          0.016      1000.000
 ITERATION COUNT, LIMIT         8    2000000000
```

---

## 5. Timeout and Edge Cases

### 5.1 Timeout Strategy

**Default timeout:** 60 seconds

**Rationale:**
- Most GAMSLIB models solve in <1 second
- 60 seconds handles larger models
- Prevents batch processing from stalling
- Models timing out are flagged for manual review

**Handling timeouts:**
```python
# Models that timeout get ERROR status
if timeout:
    status = ConvexityStatus.ERROR
    message = f"Timeout after {timeout_seconds} seconds"
```

### 5.2 Edge Case Handling

| Case | Handling | Status |
|------|----------|--------|
| Compilation error | Exit code 2 | ERROR |
| Missing .lst file | No output | ERROR |
| Multiple solves | Use last solve | Depends on last status |
| No solve statement | No status in .lst | ERROR |
| Licensing issue | MODEL STATUS 11 | ERROR |
| Evaluation error | SOLVER STATUS 5 | ERROR |
| Model too large | License limit | ERROR |

### 5.3 Infeasible and Unbounded Models

**Infeasible models (MODEL STATUS 4, 5, 6, 19):**
- Not useful for validation testing
- Excluded from corpus
- Logged for reference

**Unbounded models (MODEL STATUS 3, 18):**
- Model has no finite optimum
- Excluded from corpus
- May indicate modeling error

### 5.4 Multi-Start Verification

**Sprint 13 approach:** Single solve (no multi-start)

**Rationale:**
- Simpler implementation
- Faster batch processing
- Most GAMSLIB models are well-posed
- Multi-start is enhancement for Sprint 14+

**Future enhancement:**
```python
def multi_start_verify(model_path: str, num_starts: int = 3) -> VerificationResult:
    """
    Verify with multiple starting points.
    
    If different starts yield different objective values,
    the problem is likely non-convex.
    """
    # Implementation deferred to Sprint 14+
    pass
```

---

## 6. Batch Processing

### 6.1 Batch Execution Script

```bash
#!/bin/bash
# verify_batch.sh - Verify convexity of all models in directory

INPUT_DIR=$1
OUTPUT_CSV=$2
TIMEOUT=60

echo "model_id,model_type,convexity_status,model_status,solver_status,objective,solve_time,message" > "$OUTPUT_CSV"

for gms_file in "$INPUT_DIR"/*.gms; do
    model_id=$(basename "$gms_file" .gms)
    
    # Extract model type from file (simplified)
    model_type=$(grep -oE 'using\s+(LP|NLP|QCP|MIP|MINLP)' "$gms_file" | head -1 | awk '{print $2}')
    
    if [[ -z "$model_type" ]]; then
        model_type="UNKNOWN"
    fi
    
    # Run verification (would call Python script in practice)
    # python verify_model.py "$gms_file" "$model_type" "$TIMEOUT"
    
    echo "$model_id,$model_type,pending,,,," >> "$OUTPUT_CSV"
done
```

### 6.2 Parallel Execution

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict

def verify_batch(
    model_paths: List[str],
    model_types: Dict[str, str],
    max_workers: int = 4,
    timeout: int = 60
) -> Dict[str, VerificationResult]:
    """
    Verify multiple models in parallel.
    
    Args:
        model_paths: List of .gms file paths
        model_types: Dict mapping model_id to type
        max_workers: Number of parallel processes
        timeout: Per-model timeout in seconds
    
    Returns:
        Dict mapping model_id to VerificationResult
    """
    results = {}
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                verify_convexity,
                path,
                model_types.get(os.path.basename(path).replace('.gms', ''), 'NLP'),
                timeout
            ): path
            for path in model_paths
        }
        
        for future in as_completed(futures):
            path = futures[future]
            model_id = os.path.basename(path).replace('.gms', '')
            try:
                results[model_id] = future.result()
            except Exception as e:
                results[model_id] = VerificationResult(
                    status=ConvexityStatus.ERROR,
                    model_status=None,
                    solver_status=None,
                    objective_value=None,
                    solve_time_seconds=0.0,
                    message=str(e)
                )
    
    return results
```

---

## 7. Integration with Heuristic Detection

### 7.1 Two-Tier Approach

**Tier 1: Heuristic Pre-Check**
- Fast pattern matching (from `convexity_detection.md`)
- Detect obvious non-convex patterns
- Flag models before solving

**Tier 2: Solver-Based Verification**
- Run GAMS solver
- Check MODEL STATUS
- Classify based on result

### 7.2 Combined Algorithm

```python
def full_convexity_check(
    model_path: str,
    model_type: str,
    model_ir: Optional['ModelIR'] = None
) -> VerificationResult:
    """
    Full convexity verification with heuristic pre-check.
    """
    # Tier 1: Heuristic check (if IR available)
    if model_ir is not None:
        warnings = quick_convexity_check(model_ir)
        if warnings:
            # Model has non-convex patterns
            return VerificationResult(
                status=ConvexityStatus.NON_CONVEX,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=0.0,
                message="Heuristic detected non-convex patterns: " + "; ".join(warnings[:3])
            )
    
    # Tier 2: Solver verification
    return verify_convexity(model_path, model_type)
```

---

## 8. Summary and Recommendations

### 8.1 Sprint 13 Implementation Plan

1. **Implement `parse_gams_listing()`** - Parse .lst files
2. **Implement `verify_convexity()`** - Single model verification
3. **Implement `classify_result()`** - Status code classification
4. **Create batch script** - Process all GAMSLIB candidates
5. **Generate verification report** - CSV with all results

### 8.2 Classification Summary

| Model Type | Solver | Expected Status | Classification |
|------------|--------|-----------------|----------------|
| LP | CPLEX | MODEL STATUS 1 | `verified_convex` |
| NLP | CONOPT | MODEL STATUS 1 or 2 | `likely_convex` |
| QCP | CONOPT | MODEL STATUS 1 or 2 | `likely_convex` |
| Any | Any | MODEL STATUS 3,4,5,6 | `excluded` |
| Any | Any | SOLVER STATUS != 1 | `error` |

### 8.3 Conservative Approach

**Philosophy:** Better to exclude a convex model than include a non-convex one.

- LP: Only `verified_convex` if MODEL STATUS = 1
- NLP/QCP: `likely_convex` (not proven, but usable)
- Any doubt: `unknown` or `excluded`

### 8.4 Future Enhancements (Sprint 14+)

1. **Global solver verification** - Use BARON for definitive proof
2. **Multi-start verification** - Detect non-convexity via different optima
3. **Heuristic integration** - Combine with AST-based detection
4. **Objective comparison** - Compare nlp2mcp MCP solution with original NLP

---

## References

- GAMS Documentation: https://www.gams.com/latest/docs/
- GAMS Status Codes: https://www.gams.com/latest/docs/UG_SolverUsage.html
- `docs/research/convexity_detection.md` - Heuristic detection approach
- `docs/testing/GAMS_ENVIRONMENT_STATUS.md` - Environment setup
- Boyd & Vandenberghe, *Convex Optimization*, 2004

---

**Task 5 Status:** COMPLETE  
**Design Date:** December 30, 2025
