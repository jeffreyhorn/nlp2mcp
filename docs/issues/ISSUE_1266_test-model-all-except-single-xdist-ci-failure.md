# test_model_all_except_single: Reliable CI Failure Under Full-Suite xdist Parallelism

**GitHub Issue:** [#1266](https://github.com/jeffreyhorn/nlp2mcp/issues/1266)
**Status:** OPEN — Reproducibly failing on CI; passes locally
**Severity:** Medium — Test-only; does not block merges (main has no required status checks), but masks future regressions and poisons CI signal for every PR
**Date:** 2026-04-18
**Last Updated:** 2026-04-18
**Affected Area:** `src.ir.parser` shared state under `pytest -n auto`

---

## Problem Summary

The unit test
`tests/unit/test_sprint20_day4_grammar.py::TestSubcatL::test_model_all_except_single`
fails on every recent CI run of the `CI` workflow's `test` job. It passes
locally — even under the same `pytest -n auto -m "not slow"` command the
CI uses — on a macOS/Python 3.12.8 developer machine. The failure only
manifests on CI (Linux / Python 3.12.13 / GitHub-hosted runner).

The raised error is a parser semantic error, not a plain assertion failure:

```
src.ir.parser.ParserSemanticError: Model references unknown equation or
model 'all' [context: expression]
```

— raised from `_ModelBuilder._validate()` at `src/ir/parser.py:7362`, called
from `build()` at `src/ir/parser.py:1307`, invoked by `parse_model_text()`
at `src/ir/parser.py:423`.

The test source declares:

```gams
Variables x;
Equations eq1, eq2;
eq1.. x =e= 0;
eq2.. x =e= 1;
Model m / all - eq1 /;
```

and expects the `all - eq1` exclusion syntax to produce a model with
`eq2` only. The failure indicates the parser is treating the literal
keyword `all` as if it were a user-declared equation name rather than
the "all equations" marker — and only fails to make that distinction when
other tests have preceded it in the same xdist worker.

---

## Evidence This Is Pre-Existing, Not PR-Introduced

Every recent `main` CI run — i.e., every PR merge since Sprint 24 began —
has failed with this exact test:

| Run ID      | Merge                               | `test` job |
| ----------- | ----------------------------------- | ---------- |
| 24607660352 | PR #1264 (partssupply)              | failure    |
| 24542909528 | PR #1263 (feedtray)                 | failure    |
| 24513213293 | PR #1262 (turkey)                   | failure    |
| 24477648126 | PR #1261 (china)                    | failure    |
| 24435981236 | PR #1260 (fawley)                   | failure    |

The team has been merging past these failures because
`main` branch protection has **zero required status checks**
(`gh api repos/jeffreyhorn/nlp2mcp/branches/main/protection` →
`required_status_checks.contexts: []`). The failure signature is identical
across all runs.

---

## Reproduction

### CI (reproduces reliably)

```bash
# In GitHub Actions on ubuntu-latest with Python 3.12.13
pytest -m "not slow" -n auto -v --tb=short
# → 4444 passed, 82 skipped, 1 failed in ~37s
# FAILED tests/unit/test_sprint20_day4_grammar.py::TestSubcatL::test_model_all_except_single
```

### Locally (does **not** reproduce on macOS / Python 3.12.8)

```bash
# Full fast suite
.venv/bin/python -m pytest tests/ -n auto -m "not slow"
# → 4516 passed, 10 skipped, 1 xfailed, 13 warnings in 275.97s

# Single file under xdist
.venv/bin/python -m pytest tests/unit/test_sprint20_day4_grammar.py -v -n 4
# → 12 passed in 9.02s

# Single test in isolation
.venv/bin/python -m pytest tests/unit/test_sprint20_day4_grammar.py::TestSubcatL::test_model_all_except_single -v
# → 1 passed in 1.81s
```

The differences from CI that matter most are likely:

- Python patch version (3.12.8 vs 3.12.13)
- OS (macOS vs Linux)
- xdist worker count (CI uses whatever `-n auto` resolves to on
  GitHub-hosted runners, typically 4; local macOS 12-core also 4 but
  with different file-allocation timing)
- Full-suite file ordering (the failure only shows up when the full
  suite runs; it does not reproduce with just the owning file under `-n 4`)

---

## Suspected Root Cause

The error message — "Model references unknown equation or model 'all'" —
implies the parser's validator is looking up `all` in a symbol table of
declared equations and failing to find it. In a healthy run, the parser
treats the `all` keyword in `Model m / all - eq1 /;` as a marker meaning
"all declared equations, minus the listed exclusions" and never enters
the equation-lookup path for it.

The most likely cause is **module-level shared state in `src.ir.parser`**
(a cached Lark parser instance, a class-level symbol table, a
`functools.lru_cache`, or similar) that leaks between tests when the
full-suite load order stacks certain parser invocations onto the same
xdist worker. Candidates to audit:

- Any `@lru_cache`-decorated helpers in `src/ir/parser.py`
- Class attributes on `_ModelBuilder` that should be instance attributes
- Global singletons (e.g., a cached `Lark(...)` grammar) that could be
  affected by earlier tests mutating grammar state
- The model-subtraction-as-union fallback code path
  (the warning `Model subtraction (m - n) not fully supported;
  treating as union` is logged right before the failure)

---

## Investigation Hints

1. Start by running the full suite under `-n 1` (single worker) on Linux
   to see if the failure disappears — if it does, state leakage between
   tests on the same worker is confirmed.
2. Use `pytest --randomly-seed=…` (or bisect by file) to find a minimal
   failing test ordering. The last PASSED test before the FAILED line
   in CI logs is:
   `tests/validation/test_gams_check.py::TestGAMSValidationErrors::test_validate_nonexistent_file`
   — useful as a hint for which worker the failing test lands on.
3. Audit `src/ir/parser.py` (7362 lines) for class-level mutable state,
   global caches, and shared Lark parser instances that could be
   affected by prior tests that exercise different grammar paths.
4. A quick defensive fix that would silence CI — but not address the
   root cause — is to replace `@lru_cache` helpers with instance-scoped
   caches or to clear relevant caches in a pytest fixture.

---

## Why This Matters

Even though the failure has been merged past many times, leaving it
broken has concrete costs:

- CI is currently **red on every PR**, which trains reviewers to ignore
  failing CI — a future real regression in the same `test` job will not
  be noticed.
- Any future work to enable branch protection with required status
  checks will first need to fix this test, so the debt compounds.
- The root cause (parser shared state under parallelism) may surface
  as real bugs in other code paths later.

---

## Files Involved

- `tests/unit/test_sprint20_day4_grammar.py` (lines 6–27) — the failing test
- `src/ir/parser.py` — the source of the error (lines 423, 1307, 7362 along
  the call stack; the shared-state leak is somewhere in this file)
- `.github/workflows/ci.yml` — the CI workflow running `pytest -n auto`
