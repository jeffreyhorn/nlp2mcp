# Retention patch — keep each recorded GAMS invocation's OWN listing

**Scope: a throwaway `git worktree` only. Never committed.** Used by prep Task 7 (and available to the sprint's P2/P3 batches until schema 3.1.0 makes it unnecessary). The task branch's `git diff main...HEAD -- scripts/ src/` must stay empty.

## Why

Provenance (license edition, solver actually used) must come from the **same invocation** whose result is recorded — never from a rerun, which is a different invocation (PR #1746 review). But both solve paths delete their listing:

- `scripts/gamslib/test_solve.py::solve_mcp` writes `output.lst` inside a `tempfile.TemporaryDirectory()` and, on `TimeoutExpired`, returns from its `except` handler — the directory and the listing are gone. It also resolves its executable itself (preferring `/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams` over `PATH`), and a cold row records no input path (`mcp_file_generated` is written only after an accepted presolve retry).
- `scripts/gamslib/verify_convexity.py::verify_model` likewise writes `output.lst` in a `TemporaryDirectory`, and its `--output` JSON carries neither the solver name nor the edition.

## What the patch does

It replaces each function's `with tempfile.TemporaryDirectory() as tmpdir:` with a context manager whose **`finally`** copies the invocation's `output.lst` **and** its `_cmd.json` out of the temp directory before it is removed — so the evidence survives **every** return path: normal, `TimeoutExpired`, and other errors. `_cmd.json` (exact `cmd` — executable and input path — `cwd`, start time, and **`head_sha`**: the commit the worktree is checked out at, so Task 6's gate can require every measurement to descend from the owner-answers commit; a lookup failure records `null`, which fails that gate) is written **into the same temp directory before GAMS launches**, so a listing and its command record are **paired by construction**.

Each invocation is retained under a **unique invocation id** — `<stem>.<time_ns>.<pid>.lst` / `.cmd.json` — so repeated invocations of the same model (a presolve retry, a follow-up solve) **never overwrite** earlier evidence; the copy **refuses** to overwrite an existing destination (`FileExistsError`). With `NLP2MCP_RETAIN_LST_DIR` unset, behaviour is unchanged.

## Associating a recorded row with its own invocation

A row does not carry the invocation id, so association is by evidence, and must be **unique**:

1. Candidates are the retained invocations whose `cmd.json` input path is the file the row's outcome came from (the cold `<id>_mcp.gms`, or `<id>_mcp_presolve.gms` for a row whose outcome is `model_optimal_presolve`).
2. Classify each candidate's listing (`parse_solve_summaries` / `Attribution`, and the status/objective lines) and keep those that **match the row** — solver/model status, objective, `mcp_attribution`.
3. **Exactly one** candidate must match. Zero or several → the row has **no** provenance and its result is not recorded (never pick one).

## Usage — with fail-safe cleanup

The retained listings, and `check_mcp_solve_attribution.py`'s own work directory, contain **raw license headers**. They must not outlive the run — on success **or** failure. Extract the sanitized values first (into the results doc in your **main** checkout), and let an `EXIT` trap delete everything else:

```bash
set -e
REPO=$(git rev-parse --show-toplevel)
WTP=$(mktemp -d); WT=$WTP/wt
export NLP2MCP_RETAIN_LST_DIR=$(mktemp -d)   # retained listings: raw license headers
ATTR=$(mktemp -d)                              # pass as --workdir to check_mcp_solve_attribution.py
cleanup() { cd /; git -C "$REPO" worktree remove --force "$WT" 2>/dev/null || true
            rm -rf "$NLP2MCP_RETAIN_LST_DIR" "$ATTR" "$WTP"; }
trap cleanup EXIT INT TERM
git worktree add --detach "$WT" main && cd "$WT"
python /path/to/apply_retention_patch.py        # the script below, saved OUTSIDE the repo
# ... run the batch / verifier; check_mcp_solve_attribution.py --workdir "$ATTR" ...
# ... associate rows; write ONLY the sanitized values (edition class, solver, invocation id,
#     head_sha) into the results doc in "$REPO" -- never listing content
```

`check_mcp_solve_attribution.py` otherwise creates its own `mcp_attr_*` directory with `run-*` subdirectories (`tempfile.mkdtemp`, ~L1266–1281) that **keeps** its listings — always pass `--workdir "$ATTR"` so the trap removes it. *(Exercised: with a simulated mid-run failure the trap still removed the retention directory, the attribution directory and the worktree, and unregistered the worktree.)*

Read only the **edition classification** (Task 3's non-identifying regex) and the **solver name** from each retained listing; never commit listing content (license hygiene).

## Exercised 2026-10-12/13, in a throwaway worktree

**Tested source:** `scripts/gamslib/test_solve.py` (blob `5f5ac476f263`) and `scripts/gamslib/verify_convexity.py` (blob `5dce6807f223`) — byte-identical at `main` `912d005c` and at every commit of this branch (`git diff --name-only 912d005c HEAD -- scripts/ src/` is empty), which is what the patch's source anchors were matched against. If either blob differs where you apply it, re-run these exercises before trusting the patch.

| path | result | retained |
|---|---|---|
| `solve_mcp`, normal (`trnsport`) | success · MS 1 · obj 153.675 · `MCP-SOLVED` | listing (MODEL STATUS 1) + `cmd.json` (`Versions/Current` executable) |
| `solve_mcp`, simulated `TimeoutExpired` with a partial listing | failure · solver status 3 · `path_solve_time_limit` | the **partial** listing + `cmd.json` |
| `verify_convexity.py --model trnsport --output …` (CLI) | `verified_convex` · solver/model status 1/1 · obj 153.675 | its own listing (SOLVER CPLEX, MODEL STATUS 1) + `cmd.json` (`gams … lo=3 LP=CPLEX`) |
| **three** `solve_mcp` invocations of the **same** model (two normal, one timeout) | `MCP-SOLVED` ×2, `path_solve_time_limit` | **three distinct `<inv>` pairs, none overwritten**; each `cmd.json` paired with its own listing |
| `head_sha` recorded by both paths (`solve_mcp`, verifier CLI) | — | both `cmd.json` files carry the worktree's `HEAD` SHA (checked equal to `git rev-parse HEAD`) |

Bugs found by running it, not by reading it: the helper must import `os` itself (`test_solve.py` does not); it must sit **before** `if __name__ == "__main__":` (appended after the guard, the CLI called `main()` before the helper existed; inserted "after the imports" by heuristic, it landed inside a function); and a stem-only destination let a later invocation overwrite an earlier one's evidence (PR #1746 review) — now a unique id per invocation.

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
import contextlib as _rcl, json as _rjson, os as _ros, shutil as _rsh, tempfile as _rtmp, time as _rtime


@_rcl.contextmanager
def _retaining_tmpdir(stem):
    """Copy this invocation's output.lst + _cmd.json out on EVERY exit path, under a
    UNIQUE invocation id, so repeated invocations of the same stem never overwrite."""
    with _rtmp.TemporaryDirectory() as _d:
        try:
            yield _d
        finally:
            _r = _ros.environ.get("NLP2MCP_RETAIN_LST_DIR")
            if _r:
                _inv = f"{stem}.{_rtime.time_ns()}.{_ros.getpid()}"
                for _src, _dst in (("output.lst", f"{_inv}.lst"), ("_cmd.json", f"{_inv}.cmd.json")):
                    _s, _t = _ros.path.join(_d, _src), _ros.path.join(_r, _dst)
                    if _ros.path.exists(_s):
                        if _ros.path.exists(_t):  # never overwrite retained evidence
                            raise FileExistsError(_t)
                        _rsh.copy(_s, _t)


def _record_cmd(stem, cmd, cwd, tmpdir):
    """Written INTO this invocation's tmpdir before launch, so it is copied out with
    -- and paired by construction to -- that invocation's own listing."""
    if _ros.environ.get("NLP2MCP_RETAIN_LST_DIR"):
        with open(_ros.path.join(tmpdir, "_cmd.json"), "w") as _f:
            # head_sha: the commit the measurement ran from, so the blind-decision
            # gate can require it to DESCEND from the owner-answers commit.
            _here = _ros.path.dirname(_ros.path.abspath(__file__))
            try:
                import subprocess as _rsp
                _sha = _rsp.run(["git", "-C", _here, "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
            except Exception:
                _sha = None  # a missing SHA fails the gate; never guessed
            _rjson.dump({"stem": stem, "cmd": [str(c) for c in cmd], "cwd": str(cwd),
                         "started_ns": _rtime.time_ns(), "head_sha": _sha}, _f)
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
    t = t.replace(run_anchor, f"{indent}_record_cmd({stem_expr}, {cmd_expr}, {cwd_expr}, tmpdir)\n{run_anchor}")
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
