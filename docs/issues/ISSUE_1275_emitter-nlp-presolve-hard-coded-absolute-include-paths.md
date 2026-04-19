# Emitter: `--nlp-presolve` Writes Hard-Coded Absolute `$include` Paths

**GitHub Issue:** [#1275](https://github.com/jeffreyhorn/nlp2mcp/issues/1275)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** High — Makes every generated `_mcp_presolve.gms` artifact non-portable; blocks CI reproduction and collaborator hand-off of these files
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Area:** `src/emit/*.py` — presolve wrapper emission path
**Labels:** `sprint-25`

---

## Problem Summary

When `src.cli` is invoked with `--nlp-presolve`, the generated `<model>_mcp_presolve.gms` wrapper file contains a `$include` directive referring to the original `.gms` source using an **absolute filesystem path rooted at the developer's workstation**:

```gams
$include /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/robustlp.gms
```

These generated files are committed alongside the primary MCP output (see `data/gamslib/mcp/*_mcp_presolve.gms`), so they become part of the repository state that other collaborators and CI agents pull. Anyone without that exact directory layout cannot re-run the generated artifact, defeating the artifact's reproducibility purpose.

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/robustlp.gms --nlp-presolve \
    -o /tmp/robustlp_mcp.gms
grep -n "^\$include" /tmp/robustlp_mcp_presolve.gms
# → $include /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/robustlp.gms
```

## Affected Files (observed in PR #1273 Day 13 retest)

- `data/gamslib/mcp/robustlp_mcp_presolve.gms` (line ~143)
- `data/gamslib/mcp/chain_mcp_presolve.gms` (line ~149)
- `data/gamslib/mcp/mathopt3_mcp_presolve.gms` (line ~150)
- Any other model whose solve retries via `--nlp-presolve`

---

## Root Cause

The presolve-wrapper emitter calls `Path(source).resolve()` (or equivalent) when building the `$include` directive, producing a fully-qualified absolute path. The resolve step is appropriate for internal path handling but must be normalized — relative to the repository root, or to a configurable anchor — before being written into the emitted GAMS source.

---

## Suggested Fix

Two complementary options (pick whichever fits the codebase best):

1. **Repo-relative path with a sentinel token.** Emit `$include data/gamslib/raw/<model>.gms` when the source resolves under the repository root; GAMS resolves relative `$include` against the compiler's working directory, so users who invoke GAMS from the repo root get a working file. Downside: still requires a specific CWD.

2. **`$if exist` guard with a configurable macro.** Emit:
   ```gams
   $if not set NLP2MCP_SRC $set NLP2MCP_SRC data/gamslib/raw
   $if exist %NLP2MCP_SRC%/<model>.gms $include %NLP2MCP_SRC%/<model>.gms
   ```
   Users override with `gams ... --NLP2MCP_SRC=/some/path`. Downside: more verbose.

Implementation should:

- Compute the repo-root anchor via `Path(__file__).resolve().parents[N]` (or equivalent) during emitter setup.
- Reject absolute paths outside the anchor (since there's no portable way to reference them) — emit a warning and a commented-out include so the user knows to fill it in manually.
- Add a unit test under `tests/unit/emit/` that constructs a presolve wrapper for a fixture model and asserts the `$include` is relative.

---

## Out of Scope (Do NOT Reopen)

- The non-portable artifacts currently committed to `data/gamslib/mcp/*_presolve.gms`: those were produced by the Day 13 retest (PR #1273) under the current buggy emitter. After #1275 lands, a fresh pipeline run will regenerate them portably; no manual cleanup of the committed files is needed before then.

---

## References

- PR #1273 review comments: #3106233164, #3106233167, #3106233172, #3107085374, #3107085380, #3107085383
- Sibling Sprint 25 issues: #1276–#1280 (other emitter/translator bugs surfaced by the same Day 13 review)

---

## Estimated Effort

2–3 hours (locate emitter site + decide path-anchor strategy + regression test on a couple of models under `tmp_path`).

---

## Files Involved

- `src/emit/*.py` — presolve wrapper emission (exact file to confirm during diagnosis)
- `src/cli.py` — `--nlp-presolve` option handling (may need to pass the anchor down)
- `tests/unit/emit/` — new emitter test fixture
- `data/gamslib/mcp/*_mcp_presolve.gms` — regenerated after fix (no manual edit)
