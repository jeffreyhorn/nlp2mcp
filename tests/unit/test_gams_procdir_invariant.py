"""Every GAMS launch keeps its process directory out of the working tree.

GAMS creates a *process directory* (``225a/``, then ``225b/`` ... ``225bq/``)
in its working directory. It holds ``gamslice.dat``, a copy of the license.
GAMS deletes it on a normal exit but leaves it behind when the run is killed,
which a timeout under load does. Measured on GAMS 54.2.1 (normal exit with
``keep=1``, and ``kill -9`` mid-run):

* plain run: the process dir lands in **cwd**;
* ``ScrDir=<tmp>``: still in **cwd**. ``ScrDir`` does NOT move it, despite two
  code comments that claimed so;
* ``procDirPath=<tmp>``: inside ``<tmp>``, on both exits.

Several launchers must run from the repo root (presolve emits ``$include`` a
repo-relative path), so a temp ``cwd`` is not a general fix. ``procDirPath`` is,
because it moves only the process directory.

The rule: a function that launches GAMS passes ``procDirPath=``, unless it is
named in ``CWD_IS_A_TEMP_DIR`` and its launch passes a ``cwd=`` that is not the
repo root. The exemptions are pinned by identity, so a stale one fails too.
"""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCANNED = ("src", "scripts", "tests")
SUBPROCESS_CALLS = {"run", "Popen", "check_output", "call", "check_call"}

#: Launchers whose cwd is already a fresh temp dir, so the process dir lands
#: there and is deleted with it. ``path::qualified function``.
CWD_IS_A_TEMP_DIR = {
    "scripts/gamslib/verify_convexity.py::verify_model",
    "tests/integration/test_nlp_presolve.py::TestNLPPresolveGAMSSolve.test_bearing_solves_with_presolve",
    "tests/integration/test_nlp_presolve.py::TestNLPPresolveGAMSSolve.test_bearing_fails_without_presolve",
    "tests/validation/test_path_solver.py::_check_path_available",
    # cwd is the copied file's parent, which tests/validation/conftest.py and
    # test_isolation_invariants.py force into tmp_path.
    "tests/validation/test_path_solver.py::_solve_gams",
    "tests/validation/test_path_solver_minmax.py::_solve_gams",
}

#: The launchers this PR fixed. Pinned so that the scan provably SEES them: a
#: detector that silently stopped matching would otherwise pass vacuously.
FIXED = {
    "scripts/gamslib/test_solve.py::solve_mcp",
    "scripts/diagnostics/kkt_residual.py::run_gams",
    "scripts/diagnostics/check_presolve_divergence.py::_run_gams",
    "scripts/sprint_audit/check_mcp_solve_attribution.py::run_one",
    "scripts/ci/run_pr19_solves.py::_solve_one",
    "scripts/gamslib/batch_translate.py::validate_mcp_file",
    "src/validation/gams_check.py::validate_gams_syntax",
}

REPO_ROOT_NAMES = ("PROJECT_ROOT", "repo_root", "REPO_ROOT")


def _names_gams(expr: ast.AST) -> bool:
    """Does this expression name the GAMS executable?

    Sees through the spellings the corpus actually uses: ``"gams"``,
    ``gams_exe``, ``str(gams_exe)``, ``find_gams_executable() or "gams"``.
    The ``gamslib`` model-library tool is not GAMS and creates no process dir.
    """
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return expr.value == "gams"
    if isinstance(expr, ast.Name):
        name = expr.id.lower()
        return "gams" in name and "gamslib" not in name
    if isinstance(expr, ast.BoolOp):
        return any(_names_gams(v) for v in expr.values)
    if isinstance(expr, ast.Call):
        func = getattr(expr.func, "id", getattr(expr.func, "attr", "")).lower()
        if "gams" in func and "gamslib" not in func:
            return True
        return bool(expr.args) and _names_gams(expr.args[0])
    return False


def _is_gams_argv(node: ast.AST) -> bool:
    """A list literal whose first element names the GAMS executable."""
    return isinstance(node, ast.List) and bool(node.elts) and _names_gams(node.elts[0])


def _launches(fn: ast.AST) -> list[ast.Call]:
    return [
        n
        for n in ast.walk(fn)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr in SUBPROCESS_CALLS
        and getattr(n.func.value, "id", "") == "subprocess"
    ]


def scan(source: str, rel: str) -> dict[str, tuple[bool, list[str | None]]]:
    """``{rel::qualname: (passes procDirPath, [cwd expression per launch])}``.

    A function counts as a GAMS launcher if it both builds a GAMS argv and calls
    ``subprocess``. Nested functions are reported under their own name only.
    """
    tree = ast.parse(source)
    out: dict[str, tuple[bool, list[str | None]]] = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                own = [
                    n
                    for n in ast.walk(child)
                    if not (
                        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n is not child
                    )
                ]
                calls = _launches(child)
                if calls and any(_is_gams_argv(n) for n in own):
                    seg = ast.get_source_segment(source, child) or ""
                    cwds = [
                        next(
                            (
                                ast.get_source_segment(source, k.value)
                                for k in c.keywords
                                if k.arg == "cwd"
                            ),
                            None,
                        )
                        for c in calls
                    ]
                    out[f"{rel}::{qual}"] = ("procDirPath=" in seg, cwds)
                visit(child, f"{qual}.")

    visit(tree, "")
    return out


def _corpus() -> dict[str, tuple[bool, list[str | None]]]:
    found: dict[str, tuple[bool, list[str | None]]] = {}
    for root in SCANNED:
        for path in sorted((PROJECT_ROOT / root).rglob("*.py")):
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            found |= scan(path.read_text(encoding="utf-8"), rel)
    return found


def test_every_gams_launch_relocates_its_process_directory() -> None:
    offenders = [
        site
        for site, (has_procdir, _cwds) in _corpus().items()
        if not has_procdir and site not in CWD_IS_A_TEMP_DIR
    ]
    assert offenders == [], (
        "these functions launch GAMS without procDirPath=<tempdir>. A killed run "
        f"leaves a process dir holding a license copy in cwd: {offenders}"
    )


def test_the_scan_sees_every_fixed_launcher() -> None:
    found = _corpus()
    missing = sorted(FIXED - set(found))
    assert missing == [], f"the detector no longer recognises these launchers: {missing}"
    assert all(found[s][0] for s in FIXED)


def test_each_exemption_is_a_launcher_with_a_non_repo_cwd() -> None:
    found = _corpus()
    stale = sorted(CWD_IS_A_TEMP_DIR - set(found))
    assert stale == [], f"exemptions that no longer launch GAMS: {stale}"
    for site in CWD_IS_A_TEMP_DIR:
        cwds = found[site][1]
        assert cwds and all(c is not None for c in cwds), f"{site}: a launch without cwd="
        assert not any(
            name in c for c in cwds if c for name in REPO_ROOT_NAMES
        ), f"{site}: cwd is the repo root, so it needs procDirPath, not an exemption"


def test_the_guard_flags_a_launch_without_procdirpath() -> None:
    """Positive control: the defect this file guards against is detected."""
    leaky = (
        "import subprocess\n"
        "def solve(gams_exe, mcp, tmp):\n"
        "    subprocess.run([gams_exe, mcp, f'ScrDir={tmp}'], cwd=PROJECT_ROOT)\n"
    )
    fixed = leaky.replace("f'ScrDir={tmp}'", "f'ScrDir={tmp}', f'procDirPath={tmp}'")
    assert scan(leaky, "x.py") == {"x.py::solve": (False, ["PROJECT_ROOT"])}
    assert scan(fixed, "x.py") == {"x.py::solve": (True, ["PROJECT_ROOT"])}


def test_the_guard_ignores_non_gams_subprocesses() -> None:
    src = (
        "import subprocess\n"
        "def f():\n"
        "    subprocess.run(['which', 'gams'])\n"
        "    subprocess.run(['gamslib', 'trnsport'], cwd=d)\n"
    )
    assert scan(src, "x.py") == {}


def test_the_guard_sees_through_the_spellings_the_corpus_uses() -> None:
    """A first version saw only a bare name. It missed three real launchers,
    which the exemption check caught as "stale"."""
    for head in ("str(gams_exe)", "find_gams_executable() or 'gams'", "'gams'"):
        src = f"import subprocess\ndef f(m):\n    subprocess.run([{head}, m])\n"
        assert scan(src, "x.py") == {"x.py::f": (False, [None])}, head
