# Infrastructure: pool.gms Missing Include File (poolmod.inc)

**GitHub Issue**: #409  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/409  
**Priority**: HIGH  
**Complexity**: N/A (Infrastructure)  
**Estimated Effort**: 15 minutes  
**Tier 2 Models Blocked**: pool.gms

## Summary

The pool.gms model requires an external include file `poolmod.inc` that is not present in the test fixtures. This is not a parser limitation but a test infrastructure issue - the file needs to be downloaded from GAMSLib.

## Current Behavior

When parsing pool.gms, the parser fails with:

```
Error: Included file not found: /Users/jeff/experiments/nlp2mcp/tests/fixtures/tier2_candidates/poolmod.inc
  Referenced from: /Users/jeff/experiments/nlp2mcp/tests/fixtures/tier2_candidates/pool.gms
```

## Expected Behavior

The `poolmod.inc` file should be present in the test fixtures alongside `pool.gms` so the model can be parsed successfully.

## Root Cause

The pool.gms file contains:

```gams
$include poolmod.inc
```

This references an external file that defines:
- Additional sets, parameters, or variables
- Model equations or constraints  
- Data tables

The include file was not downloaded when pool.gms was added to test fixtures.

## Solution

### Option 1: Download Missing Include File (Recommended)

Download `poolmod.inc` from GAMSLib and add it to `tests/fixtures/tier2_candidates/`:

```bash
# From GAMSLib repository or GAMS installation
cp poolmod.inc tests/fixtures/tier2_candidates/
```

### Option 2: Inline the Include File

If the include file is small, inline its contents directly into pool.gms (less ideal for testing real-world patterns).

### Option 3: Skip pool.gms in Tests

Mark pool.gms as requiring external dependencies and skip in automated tests (least preferred).

## Implementation Steps

1. Locate poolmod.inc in GAMSLib repository
   - Check GAMS model library: https://www.gams.com/latest/gamslib_ml/libhtml/
   - Or from local GAMS installation

2. Download or copy the file to test fixtures:
   ```bash
   cd tests/fixtures/tier2_candidates/
   # Download or copy poolmod.inc here
   ```

3. Verify pool.gms now parses:
   ```bash
   python -c "from src.ir.parser import parse_model_file; parse_model_file('tests/fixtures/tier2_candidates/pool.gms')"
   ```

4. Commit both pool.gms and poolmod.inc together

## Testing Requirements

After adding poolmod.inc:
1. Verify pool.gms parses without errors
2. Check that all sets/parameters from include file are recognized
3. Ensure no circular include dependencies
4. Add to automated test suite

## Impact

**Models Unlocked**: 1 (pool.gms)  
**Parse Rate Improvement**: 55.6% → 61.1% (+5.5 percentage points)

This unblocks pool.gms without any code changes.

## Related Issues

None - this is purely a test infrastructure task, not a parser feature.

## References

- **GAMSLib Model**: pool.gms (Pooling Problem)
- **Include File**: poolmod.inc (required dependency)
- **Analysis**: Tier 2 parsing status report (2025-12-03)
- **GAMS Documentation**: $include directive for external files

## Notes

- This is categorized as "infrastructure" not "parser" since no code changes needed
- The include file mechanism itself already works in the parser
- This is just a matter of having the required test data present
- May want to document which models have external dependencies
