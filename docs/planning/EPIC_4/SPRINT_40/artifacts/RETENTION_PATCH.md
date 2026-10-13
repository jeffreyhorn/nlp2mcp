# Retention patch — keep each recorded GAMS invocation's OWN listing

**Scope: a throwaway `git worktree` only. Never committed.** Used by prep Task 7 (and available to the sprint's P2/P3 batches until schema 3.1.0 makes it unnecessary). The task branch's `git diff main...HEAD -- scripts/ src/` must stay empty.

## Why

Provenance (license edition, solver actually used) must come from the **same invocation** whose result is recorded — never from a rerun, which is a different invocation (PR #1746 review). But both solve paths delete their listing:

- `scripts/gamslib/test_solve.py::solve_mcp` writes `output.lst` inside a `tempfile.TemporaryDirectory()` and, on `TimeoutExpired`, returns from its `except` handler — the directory and the listing are gone. It also resolves its executable itself (preferring `/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams` over `PATH`), and a cold row records no input path (`mcp_file_generated` is written only after an accepted presolve retry).
- `scripts/gamslib/verify_convexity.py::verify_model` likewise writes `output.lst` in a `TemporaryDirectory`, and its `--output` JSON carries neither the solver name nor the edition.

## What the patch does

It replaces each function's `with tempfile.TemporaryDirectory() as tmpdir:` with a context manager whose **`finally`** copies `output.lst` (if present) to `$NLP2MCP_RETAIN_LST_DIR/<stem>.lst` before the directory is removed — so the listing survives **every** return path: normal, `TimeoutExpired`, and other errors. It also writes `<stem>.cmd.json` (exact `cmd` — executable and input path — and `cwd`) **before** launching GAMS. With `NLP2MCP_RETAIN_LST_DIR` unset, behaviour is unchanged.

## Usage

```bash
WT=$(mktemp -d)/wt && git worktree add --detach "$WT" main && cd "$WT"
python /path/to/apply_retention_patch.py        # the script below, saved OUTSIDE the repo
export NLP2MCP_RETAIN_LST_DIR=$(mktemp -d)
# ... run the batch / verifier here; read edition + solver from $NLP2MCP_RETAIN_LST_DIR/*.lst
cd - && git worktree remove --force "$WT"
```

Read only the **edition classification** (Task 3's non-identifying regex) and the **solver name** from each retained listing; never commit listing content (license hygiene).

## Exercised 2026-10-12, in a throwaway worktree

| path | result | retained |
|---|---|---|
| `solve_mcp`, normal (`trnsport`) | success · MS 1 · obj 153.675 · `MCP-SOLVED` | `trnsport_mcp.lst` (MODEL STATUS 1) + `cmd.json` (`Versions/Current` executable) |
| `solve_mcp`, simulated `TimeoutExpired` with a partial listing | failure · solver status 3 · `path_solve_time_limit` | the **partial** listing + `cmd.json` |
| `verify_convexity.py --model trnsport --output …` (CLI) | `verified_convex` · solver/model status 1/1 · obj 153.675 | its own `trnsport.lst` (SOLVER CPLEX, MODEL STATUS 1) + `cmd.json` (`gams … lo=3 LP=CPLEX`) |

Two bugs were found by running it, not by reading it: the helper must import `os` itself (`test_solve.py` does not), and it must be placed **before** `if __name__ == "__main__":` (appending after the guard made the CLI call `main()` before the helper existed; inserting "after the imports" by heuristic landed inside a function).

## `apply_retention_patch.py`

```python
"""SCRATCH patch for a THROWAWAY worktree only -- never committed.

Retains the ACTUAL GAMS listing (and records the exact command BEFORE launch)
for both `test_solve.py::solve_mcp` and `verify_convexity.py::verify_model`,
on every return path (normal, TimeoutExpired, other errors): the
TemporaryDirectory is wrapped in a context manager whose `finally` copies
`output.lst` before the directory is removed.

Usage (from the worktree root):  python apply_retention_patch.py
Then run with NLP2MCP_RETAIN_LST_DIR=<dir> set.
"""

from pathlib import Path

HELPER = '''
# --- SCRATCH retention helper (throwaway worktree only; never committed) ---
import contextlib as _rcl, json as _rjson, os as _ros, shutil as _rsh, tempfile as _rtmp


@_rcl.contextmanager
def _retaining_tmpdir(stem):
    with _rtmp.TemporaryDirectory() as _d:
        try:
            yield _d
        finally:
            _r = _ros.environ.get("NLP2MCP_RETAIN_LST_DIR")
            _l = _ros.path.join(_d, "output.lst")
            if _r and _ros.path.exists(_l):
                _rsh.copy(_l, _ros.path.join(_r, f"{stem}.lst"))


def _record_cmd(stem, cmd, cwd):
    _r = _ros.environ.get("NLP2MCP_RETAIN_LST_DIR")
    if _r:
        with open(_ros.path.join(_r, f"{stem}.cmd.json"), "w") as _f:
            _rjson.dump({"cmd": [str(c) for c in cmd], "cwd": str(cwd)}, _f)
# --- end SCRATCH helper ---
'''


def patch(path: str, stem_expr: str, run_anchor: str, cmd_expr: str, cwd_expr: str) -> None:
    p = Path(path)
    t = p.read_text()
    old_with = "with tempfile.TemporaryDirectory() as tmpdir:"
    assert t.count(old_with) == 1, (path, t.count(old_with))
    t = t.replace(old_with, f"with _retaining_tmpdir({stem_expr}) as tmpdir:")
    assert t.count(run_anchor) == 1, (path, run_anchor)
    indent = run_anchor[: len(run_anchor) - len(run_anchor.lstrip())]
    t = t.replace(run_anchor, f"{indent}_record_cmd({stem_expr}, {cmd_expr}, {cwd_expr})\n{run_anchor}")
    # Place at module level after all definitions: both functions only call the helper at runtime, so it
    # just has to exist by then. (Inserting "after the imports" by heuristic put it
    # inside a function whose multi-line signature closes with a column-0 ")".)
    # ...but BEFORE any `if __name__ == "__main__":` guard, or a script run as a CLI
    # (verify_convexity.py) calls main() before the helper is defined.
    guard = '\nif __name__ == "__main__":'
    if guard in t:
        i = t.rindex(guard)
        p.write_text(t[:i] + "\n" + HELPER + t[i:])
    else:
        p.write_text(t.rstrip("\n") + "\n" + HELPER)


patch(
    "scripts/gamslib/test_solve.py",
    "mcp_path.stem",
    "            subprocess.run(\n                cmd,",
    "cmd",
    "PROJECT_ROOT",
)
patch(
    "scripts/gamslib/verify_convexity.py",
    "Path(model_path).stem",
    "            result = subprocess.run(\n                [\"gams\", str(model_path_abs), f\"o={lst_path}\", \"lo=3\", solver_option],",
    "[\"gams\", str(model_path_abs), f\"o={lst_path}\", \"lo=3\", solver_option]",
    "tmpdir",
)
print("patched test_solve.py and verify_convexity.py")
```
