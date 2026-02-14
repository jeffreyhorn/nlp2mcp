# Validation: False Positive Circular Dependency Detection (ganges, gangesx)

**GitHub Issue:** [#719](https://github.com/jeffreyhorn/nlp2mcp/issues/719)
**Status:** Fixed
**Severity:** Medium — Blocks pipeline for models with mutually dependent variables across equations
**Discovered:** 2026-02-13 (Sprint 19, after Issues #714 fix advanced ganges/gangesx past level bound and model_with_list errors)
**Fixed:** 2026-02-13
**Affected Models:** ganges, gangesx

---

## Problem Summary

The model validation stage raised a false positive "Circular dependency detected" error for ganges and gangesx. The detector flagged equations `prodx` and `infalloc` as creating a circular definition between variables `x` and `g`. However, this is a valid simultaneous equation system — NLP models are solved simultaneously, so mutual dependencies between variables across equations are expected and valid.

---

## Root Cause

The `validate_no_circular_definitions` function in `src/validation/model.py` built a dependency graph from equality constraints and raised `ModelError` when cross-equation cycles were found (e.g., x -> g -> x). In NLP models solved simultaneously, such cycles are normal and valid.

---

## Fix

### Approach

Downgraded cross-equation cycle detection from an error to a debug log message. The validator still runs and logs cycles for debugging, but no longer blocks the pipeline.

### Changes

1. **`src/validation/model.py`**: Changed `validate_no_circular_definitions` to log cross-equation cycles as `logger.debug()` instead of raising `ModelError`. Updated docstring to reflect new behavior.

2. **`tests/integration/test_error_recovery.py`**: Updated `test_circular_dependency_detected` → `test_circular_dependency_not_raised` to verify cross-equation cycles are allowed.

3. **`tests/validation/test_error_messages.py`**: Updated `test_circular_dependency_message` → `test_circular_dependency_allowed` to verify no error is raised. Updated `test_maximum_message_readability` to use a constant equation error instead.

### Results

- ganges and gangesx advance past circular dependency check (now hit separate domain set issue)
- All quality gates pass (typecheck, lint, format, 3315 tests)
