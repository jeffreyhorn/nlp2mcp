# ps5_s_mn: Uninitialized Parameters from Multi-Solve Loop Pattern

**GitHub Issue:** [#944](https://github.com/jeffreyhorn/nlp2mcp/issues/944)
**Status:** FIXED (already resolved by prior Issue #917 fix)
**Models:** ps5_s_mn (GAMSlib)
**Error category:** `gams_compilation_error` (Error 141, then Error 257)
**Compilation error:** `Symbol declared but no values have been assigned`

## Description

The ps5_s_mn model uses a `loop(t, ...)` with embedded `solve` statements that populate parameters (`Util_lic`, `Util_lic2`, `MN_lic`, `pt`) used later in display/comparison logic. The NLP-to-MCP transformation cannot handle this multi-solve pattern because:

1. The parameters `pt(i,t)` are initialized via `uniform()` inside a loop — the transformer doesn't execute procedural GAMS code
2. `Util_lic(t)`, `Util_lic2(t)`, `MN_lic(t)`, `MN_lic2(t)` are populated by `.l` values from solve statements inside the loop — these values don't exist in the MCP
3. The generated MCP declares these parameters but never assigns them, causing GAMS Error 141

## Fix

The Issue #917 fix in `src/emit/original_symbols.py` (lines 858-864) already handles this case: parameters with no values AND no expressions are skipped during emission. The problematic parameters (`Util_lic`, `Util_lic2`, `MN_lic`, `MN_lic2`, `x_lic`, `x_lic2`) are no longer emitted in the MCP.

**Results:**
- Parse: OK
- Translate: OK
- GAMS compile: OK (no $141 errors)
- Solve: SOLVER STATUS 1 Normal Completion, MODEL STATUS 1 Optimal

No code changes required.
