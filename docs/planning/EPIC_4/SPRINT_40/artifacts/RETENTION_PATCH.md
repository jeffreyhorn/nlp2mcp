# Retention patch — keep EVERY recorded GAMS invocation's OWN listing

**Scope: a throwaway `git worktree` only. Never committed.** Used by prep Task 7 (and by Task 8's candidate solve). The task branch's `git diff main...HEAD -- scripts/ src/` must stay empty.

## Why

Provenance (license edition, solver actually used, the commit a measurement ran from) must come from the **same invocation** whose result is recorded — never a rerun (PR #1746 review). And it must cover **every** GAMS invocation Task 7 makes, or Task 6's blind-decision gate checks only part of the measurement. The GAMS launches in the Task-7 toolchain at `912d005c` — the complete inventory, every other `subprocess.run` in these modules launches `gdxdump`, `python -m src.cli` or `git` — are:

| site | function | produces |
|---|---|---|
| `solve_mcp` | `scripts/gamslib/test_solve.py::solve_mcp` | the MCP solve (batch rows; also `kkt_residual.py`'s cold start) |
| `verify_model` | `scripts/gamslib/verify_convexity.py::verify_model` | the convexity classification |
| `kkt_residual` | `scripts/diagnostics/kkt_residual.py::run_gams` | the residual-evaluation solve behind the `CASE_A/B/C` verdict |
| `attribution` | `scripts/sprint_audit/check_mcp_solve_attribution.py::run_one` | the standalone attribution exercise (Unknown 2.3) |

All four delete or bury their listing (temp directories; a cold row records no input path; `solve_mcp` resolves its own executable), so none of it can be reconstructed afterwards.

## What the patch does

Each GAMS-launching `subprocess.run(` becomes `_retained_run(<site>, …)`. Before launch it writes `<inv>.cmd.json` — **site**, **phase** (`$NLP2MCP_RETAIN_PHASE`, set by the executor for each tool run: `batch`, `convexity`, `residual`, `attribution`), stem, exact `cmd` (executable and input path), `cwd`, start time and **`head_sha`** (the worktree's checked-out commit; `null` on lookup failure, which fails Task 6's gate). In a **`finally`** — every return path, `TimeoutExpired` included — it copies the listing named by the `o=` argument to `<inv>.lst`. `<inv>` is `<stem>.<time_ns>.<pid>`, unique per invocation; an existing destination is never overwritten (`FileExistsError`). With `NLP2MCP_RETAIN_LST_DIR` unset, behaviour is unchanged. The script **asserts each of the four anchors exactly once** and reports the remaining (non-GAMS) `subprocess.run` calls per module — keep that output with the run.

## Completeness and association

- **Completeness:** every GAMS run in Task 7 goes through one of the four tools — **no direct `gams` calls** — and the `**Measured at:**` line lists the `head_sha` of **every** retained `cmd.json`, all sites and phases. So the SHA list covers every measurement by construction; a `null` or missing SHA fails.
- **Association — exactly one invocation per recorded value**, zero or several → no provenance, value not recorded:
  - **MCP stage** (`mcp` tuple): phase `batch`, site `solve_mcp`, input `<id>_mcp.gms` (or `<id>_mcp_presolve.gms` for a presolve outcome), whose classified listing matches the row's status, objective and `mcp_attribution`.
  - **Convexity stage** (`convexity` tuple): phase `convexity`, site `verify_model`, input `<id>.gms`, matching the verifier JSON's status.
  - **Residual stage** (`residual` tuple): phase `residual`, site `kkt_residual`, input `<id>_mcp_presolve_residual.gms` — the one residual evaluation behind the row's `kkt_residual.py` verdict (its cold-start solve, if run, is a separate `solve_mcp` invocation under phase `residual`).
  - **Attribution exercise:** phase `attribution` — not a Results-row value, but its SHAs are on the `**Measured at:**` line like every other invocation.

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
python /path/to/apply_retention_patch.py        # the script below, saved OUTSIDE the repo; keep its output
export NLP2MCP_RETAIN_PHASE=batch               # set per tool run: batch | convexity | residual | attribution
# ... run the batch / verifier; check_mcp_solve_attribution.py --workdir "$ATTR" ...
# ... associate rows; write ONLY the sanitized values (edition class, solver, invocation id,
#     head_sha) into the results doc in "$REPO" -- never listing content
```

`check_mcp_solve_attribution.py` otherwise creates its own `mcp_attr_*` directory with `run-*` subdirectories (`tempfile.mkdtemp`, ~L1266–1281) that **keeps** its listings — always pass `--workdir "$ATTR"` so the trap removes it. *(Exercised: with a simulated mid-run failure the trap still removed the retention directory, the attribution directory and the worktree, and unregistered the worktree.)*

Read only the **edition classification** (Task 3's non-identifying regex) and the **solver name** from each retained listing; never commit listing content (license hygiene).

## Exercised 2026-10-13, in a throwaway worktree

**Tested source:** `scripts/gamslib/test_solve.py` (blob `5f5ac476f263`), `scripts/gamslib/verify_convexity.py` (blob `5dce6807f223`), `scripts/diagnostics/kkt_residual.py` and `scripts/sprint_audit/check_mcp_solve_attribution.py` — all byte-identical at `main` `912d005c` and at every commit of this branch (`git diff --name-only 912d005c HEAD -- scripts/ src/` is empty). If any differs where you apply the patch, re-run these exercises first.

| path | result | retained |
|---|---|---|
| `solve_mcp`, normal (`trnsport`, phase `batch`) | `MCP-SOLVED` | listing + `cmd.json`, `head_sha` = worktree `HEAD` |
| `solve_mcp`, `TimeoutExpired` (fake intercepting only the GAMS launch) | `path_solve_time_limit` | the **partial** listing + `cmd.json`, `head_sha` = worktree `HEAD` |
| `verify_convexity.py --model trnsport` (phase `convexity`) | rc 0 | its own listing + `cmd.json` |
| `kkt_residual.py data/gamslib/raw/trnsport.gms --no-cold-start` (phase `residual`) | `CASE_A_OR_C` | the residual-evaluation listing (`trnsport_mcp_presolve_residual`) + `cmd.json` |
| `check_mcp_solve_attribution.py --models trnsport --workdir …` (phase `attribution`) | `MCP-SOLVED` | its listing (`trnsport_mcp_presolve`) + `cmd.json` |
| three `solve_mcp` invocations of the **same** model | — | three distinct `<inv>` pairs, none overwritten |

The patch reported exactly one remaining non-GAMS `subprocess.run` in `kkt_residual.py` (`gdxdump`) and one in `check_mcp_solve_attribution.py` (the `src.cli` emit), none in the other two.

Bugs found by running it, not by reading it: the helper must import its own modules (`test_solve.py` does not import `os`); it must sit **before** `if __name__ == "__main__":` (appended after it, the CLI called `main()` first; inserted "after the imports" by heuristic, it landed inside a function); stem-only destinations let a later invocation overwrite an earlier one's evidence; and the first version instrumented only two of the four GAMS-launching sites (PR #1746 review). A test that monkeypatches `subprocess.run` globally also intercepts the helper's own `git rev-parse` — the resulting `null` `head_sha` correctly fails Task 6's gate.

## `apply_retention_patch.py`

```python
"""SCRATCH patch for a THROWAWAY worktree only -- never committed.

Retains the ACTUAL GAMS listing of EVERY GAMS invocation Task 7 makes, and records
its exact command BEFORE launch, by routing each GAMS-launching `subprocess.run(`
through `_retained_run(site, cmd, **kw)`. Covered sites (the complete inventory of
GAMS launches in the Task-7 toolchain at 912d005c; the other subprocess calls in
these modules launch gdxdump, `python -m src.cli` or git, not GAMS):

  scripts/gamslib/test_solve.py::solve_mcp                     site "solve_mcp"
  scripts/gamslib/verify_convexity.py::verify_model            site "verify_model"
  scripts/diagnostics/kkt_residual.py::run_gams                site "kkt_residual"
  scripts/sprint_audit/check_mcp_solve_attribution.py::run_one site "attribution"

The listing named by the `o=` argument is copied in a `finally`, so it survives every
return path (normal, TimeoutExpired, other errors). Each invocation is retained under
a UNIQUE id (`<stem>.<time_ns>.<pid>`); an existing destination is never overwritten.
`cmd.json` records site, phase (`$NLP2MCP_RETAIN_PHASE`, set by the executor per tool
run -- e.g. `batch`, `residual`, `attribution`), cmd, cwd, start time and head_sha.

Usage (from the worktree root):  python apply_retention_patch.py
Then run with NLP2MCP_RETAIN_LST_DIR=<dir> (and NLP2MCP_RETAIN_PHASE=<phase>) set.
"""

import re
from pathlib import Path

HELPER = '''
# --- SCRATCH retention helper (throwaway worktree only; never committed) ---
def _retained_run(_site, _cmd, **_kw):
    """subprocess.run for a GAMS launch, retaining its listing + exact command."""
    import json as _j, os as _o, shutil as _s, subprocess as _sp, time as _t
    _r = _o.environ.get("NLP2MCP_RETAIN_LST_DIR")
    if not _r:
        return _sp.run(_cmd, **_kw)
    _args = [str(_a) for _a in _cmd]
    _stem = _o.path.splitext(_o.path.basename(_args[1]))[0]
    _inv = f"{_stem}.{_t.time_ns()}.{_o.getpid()}"
    _here = _o.path.dirname(_o.path.abspath(__file__))
    try:
        _sha = _sp.run(["git", "-C", _here, "rev-parse", "HEAD"], capture_output=True,
                       text=True, check=True).stdout.strip()
    except Exception:
        _sha = None  # a missing SHA fails Task 6's gate; never guessed
    _meta = {"site": _site, "phase": _o.environ.get("NLP2MCP_RETAIN_PHASE"),
             "stem": _stem, "cmd": _args, "cwd": str(_kw.get("cwd") or _o.getcwd()),
             "started_ns": _t.time_ns(), "head_sha": _sha}
    _cj = _o.path.join(_r, f"{_inv}.cmd.json")
    if _o.path.exists(_cj):
        raise FileExistsError(_cj)
    with open(_cj, "w") as _f:          # written BEFORE launch
        _j.dump(_meta, _f)
    _lst = next((_a[2:] for _a in _args if _a.startswith("o=")), None)
    try:
        return _sp.run(_cmd, **_kw)
    finally:                            # every exit path, incl. TimeoutExpired
        if _lst and _o.path.exists(_lst):
            _t2 = _o.path.join(_r, f"{_inv}.lst")
            if _o.path.exists(_t2):
                raise FileExistsError(_t2)
            _s.copy(_lst, _t2)
# --- end SCRATCH helper ---
'''

SITES = [
    ("scripts/gamslib/test_solve.py", "solve_mcp",
     "            subprocess.run(\n                cmd,"),
    ("scripts/gamslib/verify_convexity.py", "verify_model",
     "            result = subprocess.run(\n                [\"gams\", str(model_path_abs),"),
    ("scripts/diagnostics/kkt_residual.py", "kkt_residual",
     "    proc = subprocess.run(\n        [\n            gams_exe,"),
    ("scripts/sprint_audit/check_mcp_solve_attribution.py", "attribution",
     "                proc = subprocess.run(\n                    [\n                        gams,"),
]

for path, site, anchor in SITES:
    p = Path(path)
    t = p.read_text()
    assert t.count(anchor) == 1, (path, "anchor count", t.count(anchor))
    t = t.replace(anchor, anchor.replace("subprocess.run(", f"_retained_run({site!r}, ", 1))
    guard = '\nif __name__ == "__main__":'
    if guard in t:  # before the guard, or a CLI calls main() before the helper exists
        i = t.rindex(guard)
        t = t[:i] + "\n" + HELPER + t[i:]
    else:
        t = t.rstrip("\n") + "\n" + HELPER
    p.write_text(t)
    # Report what is left: every remaining subprocess.run must be a non-GAMS launch.
    rest = len(re.findall(r"subprocess\.run\(", t))
    print(f"{path}: wrapped site {site!r}; {rest} other subprocess.run call(s) left "
          "(expected non-GAMS: gdxdump / src.cli / git -- check them)")
print("patched 4 GAMS-launching sites")
```
