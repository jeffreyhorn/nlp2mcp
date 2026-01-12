# Test Filtering Requirements for Sprint 15

**Task:** Sprint 15 Prep Task 7  
**Date:** January 12, 2026  
**Purpose:** Define comprehensive filtering requirements for `run_full_test.py` to enable selective testing during development and debugging

---

## Executive Summary

This document specifies the filtering capabilities needed for Sprint 15's `run_full_test.py` pipeline runner. Without filtering, every test run processes all 160+ models, which is inefficient for development and debugging workflows.

**Key Capabilities:**
- Model selection (single model, by type, by convexity status, random sample)
- Status-based filtering (parse success/failure, translate success/failure, solve success/failure)
- Error-based filtering (by error category)
- Stage control (run only specific stages, skip stages)
- Convenience shortcuts (only failing, skip completed, quick test)

**Existing Filtering (Sprint 14):**
- `batch_parse.py`: `--model`, `--limit`, `--dry-run`, `--verbose`
- `batch_translate.py`: `--model`, `--limit`, `--dry-run`, `--verbose`

**Sprint 15 Additions:** 20+ new filter arguments for comprehensive workflow support.

---

## 1. Use Case Catalog

### 1.1 Development Use Cases

| Use Case | Description | Proposed Filter |
|----------|-------------|-----------------|
| D1: Test single model | Debug a specific model during development | `--model=trnsport` |
| D2: Test small subset | Quick validation with limited models | `--limit=10` |
| D3: Test by type | Run only LP models, or only NLP | `--type=LP` |
| D4: Test convex models | Run only verified_convex models | `--convexity=verified_convex` |
| D5: Random sample | Quick smoke test with random models | `--random=5` |
| D6: Test new parse code | Run parse only, skip translate/solve | `--only-parse` |

### 1.2 Debugging Use Cases

| Use Case | Description | Proposed Filter |
|----------|-------------|-----------------|
| G1: Re-run failures | Re-test only models that failed | `--only-failing` |
| G2: Debug parse errors | Run models that failed parsing | `--parse-failure` |
| G3: Debug specific error | Run models with specific error type | `--error-category=syntax_error` |
| G4: Compare stages | Run models that parse but fail translate | `--parse-success --translate-failure` |
| G5: Investigate mismatch | Run models with objective mismatch | `--comparison-mismatch` |

### 1.3 Incremental Testing Use Cases

| Use Case | Description | Proposed Filter |
|----------|-------------|-----------------|
| I1: Skip completed | Don't re-test successful models | `--skip-completed` |
| I2: Only untested | Run models never tested | `--not-tested` |
| I3: Re-run with new version | Force re-run all models | `--force` |
| I4: Continue partial run | Resume from where we left off | `--skip-completed` |

### 1.4 Stage-Specific Use Cases

| Use Case | Description | Proposed Filter |
|----------|-------------|-----------------|
| S1: Parse only | Run only parse stage | `--only-parse` |
| S2: Translate only | Run only translate stage | `--only-translate` |
| S3: Solve only | Run only solve stage | `--only-solve` |
| S4: Skip solve | Run parse + translate, skip solve | `--skip-solve` |
| S5: Compare only | Run solution comparison on existing results | `--only-compare` |

### 1.5 Combination Use Cases

| Use Case | Description | Proposed Filter |
|----------|-------------|-----------------|
| C1: LP failures | Test LP models that failed | `--type=LP --only-failing` |
| C2: First 10 NLP | Quick NLP test | `--type=NLP --limit=10` |
| C3: Parse syntax errors | Re-run models with syntax errors | `--parse-failure --error-category=syntax_error` |
| C4: Convex parse test | Test verified_convex models, parse only | `--convexity=verified_convex --only-parse` |

---

## 2. Filter API Specification

### 2.1 Model Selection Filters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--model=NAME` | string | None | Process single model by ID |
| `--type=TYPE` | enum | None | Filter by GAMS type: LP, NLP, QCP |
| `--convexity=STATUS` | enum | None | Filter by convexity: verified_convex, likely_convex |
| `--limit=N` | int | None | Process only first N models (after other filters) |
| `--random=N` | int | None | Process N random models (after other filters) |
| `--exclude=NAME` | string | None | Exclude specific model(s), comma-separated |

### 2.2 Status Filters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--parse-success` | flag | False | Only models that parsed successfully |
| `--parse-failure` | flag | False | Only models that failed parsing |
| `--translate-success` | flag | False | Only models that translated successfully |
| `--translate-failure` | flag | False | Only models that failed translation |
| `--solve-success` | flag | False | Only models that solved successfully |
| `--solve-failure` | flag | False | Only models that failed solving |
| `--not-tested` | flag | False | Only models never tested (status = not_tested) |

### 2.3 Error Filters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--error-category=CAT` | string | None | Models with specific error category |
| `--parse-error=CAT` | string | None | Models with specific parse error |
| `--translate-error=CAT` | string | None | Models with specific translation error |
| `--solve-error=CAT` | string | None | Models with specific solve error |
| `--comparison-mismatch` | flag | False | Models with objective mismatch |
| `--comparison-match` | flag | False | Models with objective match |

### 2.4 Stage Control Filters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--only-parse` | flag | False | Run only parse stage |
| `--only-translate` | flag | False | Run only translate stage (requires parse success) |
| `--only-solve` | flag | False | Run only solve stage (requires translate success) |
| `--only-compare` | flag | False | Run only comparison (requires both NLP and MCP solutions) |
| `--skip-parse` | flag | False | Skip parse stage (use existing results) |
| `--skip-translate` | flag | False | Skip translate stage |
| `--skip-solve` | flag | False | Skip solve stage |
| `--skip-compare` | flag | False | Skip comparison stage |

### 2.5 Convenience Filters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--only-failing` | flag | False | Shorthand: any stage has failure status |
| `--skip-completed` | flag | False | Skip models where all stages succeeded |
| `--quick` | flag | False | Shorthand for `--limit=10` |
| `--force` | flag | False | Force re-run even if already completed |

### 2.6 Output Control

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dry-run` | flag | False | Show what would be done without executing |
| `--verbose` | flag | False | Show detailed output for each model |
| `--quiet` | flag | False | Suppress progress output, show only summary |
| `--json` | flag | False | Output results as JSON |
| `--save-every=N` | int | 10 | Save database every N models |

---

## 3. Filter Combination Logic

### 3.1 AND Logic (Default)

Multiple filters combine with AND logic. All filters must match for a model to be included.

**Example:**
```bash
# Both conditions must be true:
# - Model type is LP
# - Parse status is failure
python run_full_test.py --type=LP --parse-failure

# Results: Only LP models that failed parsing
```

### 3.2 Implicit Requirements

Some filters imply requirements from earlier stages:

| Filter | Implied Requirement |
|--------|---------------------|
| `--only-translate` | Model must have parse success |
| `--only-solve` | Model must have translate success |
| `--only-compare` | Model must have NLP solution (from convexity) AND MCP solution |
| `--translate-failure` | Model must have been attempted (parse success) |
| `--solve-failure` | Model must have been attempted (translate success) |

### 3.3 Conflict Detection

The following filter combinations are conflicts and should produce an error:

| Conflict | Reason |
|----------|--------|
| `--parse-success --parse-failure` | Mutually exclusive |
| `--translate-success --translate-failure` | Mutually exclusive |
| `--solve-success --solve-failure` | Mutually exclusive |
| `--only-parse --only-translate` | Can only run one stage with --only-* |
| `--only-parse --only-solve` | Can only run one stage with --only-* |
| `--only-translate --only-solve` | Can only run one stage with --only-* |
| `--only-parse --only-compare` | Can only run one stage with --only-* |
| `--only-translate --only-compare` | Can only run one stage with --only-* |
| `--only-solve --only-compare` | Can only run one stage with --only-* |
| `--skip-parse --only-parse` | Cannot skip and only-run same stage |
| `--skip-translate --only-translate` | Cannot skip and only-run same stage |
| `--skip-solve --only-solve` | Cannot skip and only-run same stage |
| `--skip-compare --only-compare` | Cannot skip and only-run same stage |
| `--comparison-match --comparison-mismatch` | Mutually exclusive |

### 3.4 Filter Precedence

Filters are applied in this order:
1. **Model selection** (`--model`, `--type`, `--convexity`, `--exclude`)
2. **Status filters** (`--parse-success`, `--only-failing`, etc.)
3. **Error filters** (`--error-category`, etc.)
4. **Limit/random** (`--limit`, `--random`)

This ensures `--limit` applies after all other filters.

---

## 4. Implementation Guidelines

### 4.1 Database Query Pattern

```python
def filter_models(db: dict, args: argparse.Namespace) -> list[dict]:
    """Apply filters to model list and return matching models."""
    models = db['models']
    
    # Phase 1: Model selection
    if args.model:
        models = [m for m in models if m['model_id'] == args.model]
    if args.type:
        models = [m for m in models if m['gamslib_type'] == args.type]
    if args.convexity:
        models = [m for m in models 
                  if m.get('convexity', {}).get('status') == args.convexity]
    if args.exclude:
        excluded = set(args.exclude.split(','))
        models = [m for m in models if m['model_id'] not in excluded]
    
    # Phase 2: Status filters
    if args.parse_success:
        models = [m for m in models 
                  if m.get('nlp2mcp_parse', {}).get('status') == 'success']
    if args.parse_failure:
        models = [m for m in models 
                  if m.get('nlp2mcp_parse', {}).get('status') == 'failure']
    if args.only_failing:
        models = [m for m in models if _has_any_failure(m)]
    if args.skip_completed:
        models = [m for m in models if not _is_fully_completed(m)]
    
    # Phase 3: Error filters
    if args.error_category:
        models = [m for m in models if _has_error_category(m, args.error_category)]
    
    # Phase 4: Limit/random (applied last)
    if args.random:
        import random
        models = random.sample(models, min(args.random, len(models)))
    elif args.limit:
        models = models[:args.limit]
    
    return models


def _has_any_failure(model: dict) -> bool:
    """Check if model has any failure status."""
    parse = model.get('nlp2mcp_parse', {}).get('status')
    translate = model.get('nlp2mcp_translate', {}).get('status')
    solve = model.get('mcp_solve', {}).get('status')
    compare = model.get('solution_comparison', {}).get('comparison_status')
    
    return any([
        parse == 'failure',
        translate == 'failure',
        solve == 'failure',
        compare == 'mismatch'
    ])


def _is_fully_completed(model: dict) -> bool:
    """Check if all stages completed successfully."""
    parse = model.get('nlp2mcp_parse', {}).get('status')
    translate = model.get('nlp2mcp_translate', {}).get('status')
    solve = model.get('mcp_solve', {}).get('status')
    compare = model.get('solution_comparison', {}).get('comparison_status')
    
    return all([
        parse == 'success',
        translate == 'success',
        solve == 'success',
        compare == 'match'
    ])


def _has_error_category(model: dict, category: str) -> bool:
    """Check if model has specific error category in any stage."""
    for stage in ['nlp2mcp_parse', 'nlp2mcp_translate', 'mcp_solve']:
        error = model.get(stage, {}).get('error', {})
        if error.get('category') == category:
            return True
    return False
```

### 4.2 Conflict Detection

```python
def validate_filters(args: argparse.Namespace) -> None:
    """Validate filter arguments for conflicts."""
    conflicts = []
    
    # Mutually exclusive status pairs
    if args.parse_success and args.parse_failure:
        conflicts.append("--parse-success and --parse-failure are mutually exclusive")
    if args.translate_success and args.translate_failure:
        conflicts.append("--translate-success and --translate-failure are mutually exclusive")
    if args.solve_success and args.solve_failure:
        conflicts.append("--solve-success and --solve-failure are mutually exclusive")
    if args.comparison_match and args.comparison_mismatch:
        conflicts.append("--comparison-match and --comparison-mismatch are mutually exclusive")
    
    # Only-* stage conflicts
    only_flags = [args.only_parse, args.only_translate, args.only_solve, args.only_compare]
    if sum(only_flags) > 1:
        conflicts.append("Only one --only-* flag can be specified")
    
    # Skip and only conflicts
    if args.skip_parse and args.only_parse:
        conflicts.append("Cannot use --skip-parse with --only-parse")
    if args.skip_translate and args.only_translate:
        conflicts.append("Cannot use --skip-translate with --only-translate")
    if args.skip_solve and args.only_solve:
        conflicts.append("Cannot use --skip-solve with --only-solve")
    if args.skip_compare and args.only_compare:
        conflicts.append("Cannot use --skip-compare with --only-compare")
    
    if conflicts:
        raise ValueError("Filter conflicts:\n" + "\n".join(f"  - {c}" for c in conflicts))
```

### 4.3 Reporting Format

```python
def report_filter_summary(models: list[dict], args: argparse.Namespace, total: int) -> None:
    """Report filter results before processing."""
    filters_applied = []
    
    if args.model:
        filters_applied.append(f"model={args.model}")
    if args.type:
        filters_applied.append(f"type={args.type}")
    if args.parse_success:
        filters_applied.append("parse-success")
    if args.only_failing:
        filters_applied.append("only-failing")
    if args.limit:
        filters_applied.append(f"limit={args.limit}")
    
    if filters_applied:
        print(f"Filters applied: {', '.join(filters_applied)}")
    
    print(f"Selected {len(models)} of {total} models")
    
    if total - len(models) > 0:
        print(f"Skipped {total - len(models)} models due to filters")
```

---

## 5. Cascading Failure Handling

### 5.1 Pipeline Stage Dependencies

The pipeline has strict stage dependencies:

```
Parse → Translate → Solve → Compare
```

If an upstream stage fails, downstream stages cannot proceed.

### 5.2 Cascade Behavior

| Upstream Status | Downstream Behavior |
|-----------------|---------------------|
| `parse.status = failure` | `translate.status = not_tested`, `solve.status = not_tested` |
| `parse.status = success`, `translate.status = failure` | `solve.status = not_tested` |
| NLP solution not available | `comparison.status = skipped` |
| MCP solution not available | `comparison.status = skipped` |

### 5.3 Skip vs. Not Tested

| Status | Meaning |
|--------|---------|
| `not_tested` | Stage was never attempted |
| `skipped` | Stage was intentionally skipped (e.g., comparison when NLP unavailable) |

### 5.4 Resumption Behavior

When using `--skip-completed`:
- Models with all stages successful are skipped entirely
- Models with partial completion continue from the last failed stage
- Models never tested start from the beginning

When using `--only-*` flags:
- `--only-translate` runs translate only on models with `parse.status = success`
- `--only-solve` runs solve only on models with `translate.status = success`
- Models not meeting prerequisites are skipped with a warning

---

## 6. Summary Statistics

### 6.1 Per-Run Statistics

After each pipeline run, report:

```
=== Pipeline Summary ===
Models processed: 34
Time elapsed: 2m 45s

Parse Results:
  Success: 34 (100.0%)
  Failure: 0 (0.0%)
  Skipped: 0 (0.0%)
  Avg time: 0.95s

Translate Results:
  Success: 32 (94.1%)
  Failure: 2 (5.9%)
  Skipped: 0 (0.0%)
  Avg time: 0.32s

Solve Results:
  Success: 30 (93.8%)
  Failure: 2 (6.3%)
  Skipped: 2 (parse/translate failed)
  Avg time: 0.15s

Comparison Results:
  Match: 28 (93.3%)
  Mismatch: 2 (6.7%)
  Skipped: 4 (no NLP/MCP solution)

Top Error Categories:
  1. syntax_error: 2 models
  2. unsupported_feature: 1 model

Full pipeline success: 28/34 (82.4%)
```

### 6.2 Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Table | (default) | Human-readable table format |
| JSON | `--json` | Machine-readable JSON output |
| Quiet | `--quiet` | Only final success rate |
| Verbose | `--verbose` | Per-model details |

### 6.3 Statistics by Model Type

When filtering by type, include breakdown:

```
Results by Type:
  LP:  5/10 (50.0%)
  NLP: 20/24 (83.3%)
  QCP: 3/3 (100.0%)
```

---

## 7. Usage Examples

### Example 1: Test single model
```bash
python run_full_test.py --model=trnsport --verbose
# Runs full pipeline on 'trnsport' model with detailed output
```

### Example 2: Quick smoke test
```bash
python run_full_test.py --quick
# Equivalent to --limit=10, runs first 10 models
```

### Example 3: Debug parse failures
```bash
python run_full_test.py --parse-failure --only-parse --verbose
# Re-runs parse on all models that previously failed parsing
```

### Example 4: Test LP models only
```bash
python run_full_test.py --type=LP
# Runs full pipeline on all LP models (57 models)
```

### Example 5: Re-run only failing models
```bash
python run_full_test.py --only-failing
# Runs models where any stage has failure status
```

### Example 6: Skip already-successful models
```bash
python run_full_test.py --skip-completed
# Skips models where all stages passed, runs others
```

### Example 7: Test with random sample
```bash
python run_full_test.py --random=5
# Runs 5 randomly selected models
```

### Example 8: Parse only, verified convex
```bash
python run_full_test.py --convexity=verified_convex --only-parse
# Parses only verified_convex models (57 models)
```

### Example 9: Debug syntax errors
```bash
python run_full_test.py --parse-failure --error-category=syntax_error --verbose
# Re-runs parse on models with syntax_error category
```

### Example 10: Combination filter
```bash
python run_full_test.py --type=NLP --parse-success --translate-failure
# NLP models that parse but fail translation
```

### Example 11: Dry run to preview
```bash
python run_full_test.py --type=LP --parse-failure --dry-run
# Shows which LP models would be re-parsed, without running
```

### Example 12: Full pipeline with limit
```bash
python run_full_test.py --limit=20 --save-every=5
# Runs 20 models, saves every 5
```

### Example 13: Translate and solve only
```bash
python run_full_test.py --skip-parse --parse-success
# Skips parse, runs translate+solve on previously parsed models
```

### Example 14: Force re-run all
```bash
python run_full_test.py --force
# Re-runs all models regardless of previous status
```

### Example 15: JSON output for CI
```bash
python run_full_test.py --quiet --json > results.json
# Minimal output, JSON format for CI integration
```

---

## 8. Sprint 15 Scope

### 8.1 MVP Filter Set (Must Have)

These filters are essential for Sprint 15:

| Filter | Priority | Justification |
|--------|----------|---------------|
| `--model=NAME` | Critical | Debug single model (already exists) |
| `--limit=N` | Critical | Quick testing (already exists) |
| `--dry-run` | Critical | Preview without executing (already exists) |
| `--verbose` | Critical | Detailed output (already exists) |
| `--type=TYPE` | High | Filter by model type |
| `--only-parse` | High | Stage-specific testing |
| `--only-translate` | High | Stage-specific testing |
| `--only-solve` | High | Stage-specific testing |
| `--only-failing` | High | Re-run failures |
| `--skip-completed` | High | Incremental testing |
| `--parse-success` | High | Filter by status |
| `--parse-failure` | High | Filter by status |
| `--translate-success` | High | Filter by status |
| `--translate-failure` | High | Filter by status |

### 8.2 Nice-to-Have (Sprint 16+)

These filters can be deferred:

| Filter | Priority | Reason for Deferral |
|--------|----------|---------------------|
| `--random=N` | Medium | Less common use case |
| `--convexity=STATUS` | Medium | Can use --type as proxy |
| `--error-category=CAT` | Medium | Requires error taxonomy integration |
| `--comparison-match/mismatch` | Medium | Solve testing specific |
| `--only-compare` | Low | Edge case |
| `--exclude=NAME` | Low | Rare use case |
| `--json` | Low | Can defer structured output |

### 8.3 Implementation Effort Estimates

| Component | Effort | Notes |
|-----------|--------|-------|
| Argument parsing | 2h | argparse setup |
| Filter logic | 3h | Model filtering functions |
| Conflict detection | 1h | Validation logic |
| Cascade handling | 2h | Stage dependency logic |
| Summary statistics | 2h | Reporting functions |
| Testing | 2h | Unit tests for filters |
| **Total** | **12h** | ~1.5 days |

---

## 9. Appendix: Existing Filter Compatibility

### 9.1 batch_parse.py Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `--model` | Keep | Works as-is |
| `--limit` | Keep | Works as-is |
| `--dry-run` | Keep | Works as-is |
| `--verbose` | Keep | Works as-is |
| `--save-every` | Keep | Works as-is |

### 9.2 batch_translate.py Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `--model` | Keep | Works as-is |
| `--limit` | Keep | Works as-is |
| `--dry-run` | Keep | Works as-is |
| `--verbose` | Keep | Works as-is |
| `--save-every` | Keep | Works as-is |

### 9.3 New run_full_test.py

The new `run_full_test.py` should:
1. Accept all existing filters from batch scripts
2. Add new Sprint 15 filters
3. Maintain backward compatibility with existing workflows
4. Support all three stages (parse, translate, solve) plus comparison
