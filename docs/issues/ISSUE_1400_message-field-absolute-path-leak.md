# gamslib DB `message` field leaks the runner's absolute home path (warning text)

**GitHub Issue:** [#1400](https://github.com/jeffreyhorn/nlp2mcp/issues/1400)
**Status:** **RESOLVED (Sprint 28 Day 11, 2026-06-19).** *(The `mcp_file_used` absolute-path leak was fixed Sprint 27 Day 13 via `_repo_relative_path`; this is the follow-on "second leak" — the captured WARNING TEXT — deferred from that day.)*
**Severity:** Low — byte-stability/portability of the recorded DB (no runtime effect); breaks cross-machine byte-identical `gamslib_status.json`.
**Affected:** any model that emits a `UserWarning` during translation (e.g. mine's `pr`-equation set-membership warning).

## Problem

`scripts/gamslib/batch_translate.py` runs the CLI as a subprocess and captures its **stderr** into the DB `message` field. Python's default `warnings.formatwarning` embeds the **absolute** source filename, e.g.:

```
/Users/<user>/experiments/nlp2mcp/src/ad/index_mapping.py:648: UserWarning: Failed to evaluate condition for equation 'pr': …
```

So the recorded `message` leaks the runner's home directory, defeating byte-identical cross-machine DB comparison (the same goal #1400's `mcp_file_used` fix served).

## Fix

`src/cli.py`: `_install_repo_relative_formatwarning()` (called at the start of `main()`) wraps `warnings.formatwarning` so an **in-repo** filename is emitted relative to the repo root (`src/ad/index_mapping.py:648`); out-of-repo paths (e.g. site-packages) are left absolute. Idempotent. The CLI subprocess therefore writes repo-relative warning text to stderr, so the captured `message` is portable.

## Verification

- `python -m src.cli data/gamslib/raw/mine.gms -o /tmp/x.gms --skip-convexity-check 2>&1 | grep -c '/Users/'` → **0** (was 4).
- `tests/unit/test_cli_repo_relative_warnings.py` (3 tests: in-repo relativized; out-of-repo absolute; idempotent).

## Related
- #1400 (`mcp_file_used` relativization, Sprint 27 Day 13) — the first leak; this doc is the message-field follow-on.
