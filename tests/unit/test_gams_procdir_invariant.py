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

The rule: every GAMS launch's ACTUAL argv carries ``procDirPath=<name>``, where
``<name>`` is bound by a ``tempfile.TemporaryDirectory()`` WITHOUT ``dir=`` in
the same function. Reusing a scratch dir does not count: four launchers' scratch
dirs lived inside the checkout, one of them retained on failure (PR #1760
review). The exception is a launcher named in ``CWD_IS_A_TEMP_DIR`` whose launch
passes a ``cwd=`` that is not the repo root. The exemptions are pinned by
identity, so a stale one fails too.
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
    "scripts/gamslib/verify_convexity.py::_run_verification",
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


def _pos(node: ast.AST) -> tuple[int, int]:
    return (getattr(node, "lineno", 0), getattr(node, "col_offset", 0))


def _external_tempdirs(fn: ast.AST, call: ast.Call) -> set[str]:
    """Names bound by a ``with tempfile.TemporaryDirectory(...) as NAME`` that
    has no ``dir=`` AND whose body contains ``call``, so the directory exists at
    that launch. A ``dir=PROJECT_ROOT`` temp dir does not qualify: a kill of the
    caller skips its cleanup. Nor does a name from a ``with`` that ``call`` is
    not inside: that directory is already deleted, or not yet made (PR #1760
    review)."""
    names: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        if not any(c is call for stmt in node.body for c in ast.walk(stmt)):
            continue
        for item in node.items:
            ctx = item.context_expr
            if (
                isinstance(ctx, ast.Call)
                and getattr(ctx.func, "attr", "") == "TemporaryDirectory"
                and not any(k.arg == "dir" for k in ctx.keywords)
                and isinstance(item.optional_vars, ast.Name)
            ):
                names.add(item.optional_vars.id)
    return names


def _argv(
    fn: ast.AST,
    arg: ast.AST,
    at: tuple[int, int],
    seen: frozenset[tuple[str, tuple[int, int]]] = frozenset(),
) -> list[ast.AST]:
    """The elements ``arg`` can hold when the statement at position ``at`` runs.

    Resolved through the forms the corpus uses: a list literal, ``[*cmd, ...]``,
    ``a + b``, and a name. A name resolves to its LAST assignment before ``at``,
    plus the ``+=`` / ``.append`` / ``.extend`` between that assignment and
    ``at``. A mutation AFTER the launch must not protect it: an earlier version
    took every mutation in the function, so ``run(cmd)`` followed by
    ``cmd.append(procDirPath)`` and a second ``run(cmd)`` reported BOTH
    launches as protected (PR #1760 review).

    This is straight-line resolution. Branches are not told apart: an
    assignment in either arm of an ``if`` counts. In ``cmd = cmd + [...]`` the
    right-hand ``cmd`` resolves at the assignment's OWN position, i.e. to the
    assignment before it. Every recursion moves to a strictly earlier position,
    so it terminates; ``seen`` (name, position) is a second guard.
    """
    if isinstance(arg, ast.List):
        out: list[ast.AST] = []
        for elt in arg.elts:
            out.extend(_argv(fn, elt.value, at, seen) if isinstance(elt, ast.Starred) else [elt])
        return out
    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
        return _argv(fn, arg.left, at, seen) + _argv(fn, arg.right, at, seen)
    if not isinstance(arg, ast.Name) or (arg.id, at) in seen:
        return []
    seen = seen | {(arg.id, at)}
    assigns = sorted(
        (
            n
            for n in ast.walk(fn)
            if isinstance(n, ast.Assign)
            and _pos(n) < at
            and any(isinstance(tg, ast.Name) and tg.id == arg.id for tg in n.targets)
        ),
        key=_pos,
    )
    if not assigns:
        return []
    base = assigns[-1]
    out = _argv(fn, base.value, _pos(base), seen)
    for node in sorted(ast.walk(fn), key=_pos):
        if not (_pos(base) < _pos(node) < at):
            continue
        if isinstance(node, ast.AugAssign) and getattr(node.target, "id", "") == arg.id:
            out.extend(_argv(fn, node.value, _pos(node), seen))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and getattr(node.func.value, "id", "") == arg.id
            and node.func.attr in ("append", "extend")
            and node.args
        ):
            a = node.args[0]
            out.extend(_argv(fn, a, _pos(node), seen) if node.func.attr == "extend" else [a])
    return out


def _procdir_value(elt: ast.AST) -> ast.AST | None:
    """The expression after ``procDirPath=`` in an argv element, if any."""
    if isinstance(elt, ast.JoinedStr) and len(elt.values) == 2:
        head, value = elt.values
        if isinstance(head, ast.Constant) and head.value == "procDirPath=":
            return value.value if isinstance(value, ast.FormattedValue) else None
    return None


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
    """``{rel::qualname: (every GAMS launch relocates its process dir, [cwd per launch])}``.

    A GAMS launch is a ``subprocess`` call whose RESOLVED argv starts with the
    GAMS executable. It relocates its process dir only if that argv itself
    carries ``procDirPath=<name>``, with ``<name>`` bound to an external temp
    dir in the same function. The function's source text is never searched:
    a docstring that mentions ``procDirPath=`` is not an argument (PR #1760
    review). Nested functions are reported under their own name.
    """
    tree = ast.parse(source)
    out: dict[str, tuple[bool, list[str | None]]] = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                launches: list[tuple[bool, str | None]] = []
                for call in _launches(child):
                    external = _external_tempdirs(child, call)
                    argv = _argv(child, call.args[0], _pos(call)) if call.args else []
                    if not argv or not _names_gams(argv[0]):
                        continue
                    values = [v for v in map(_procdir_value, argv) if v is not None]
                    ok = any(isinstance(v, ast.Name) and v.id in external for v in values)
                    cwd = next(
                        (
                            ast.get_source_segment(source, k.value)
                            for k in call.keywords
                            if k.arg == "cwd"
                        ),
                        None,
                    )
                    launches.append((ok, cwd))
                if launches:
                    out[f"{rel}::{qual}"] = (
                        all(ok for ok, _ in launches),
                        [cwd for _, cwd in launches],
                    )
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
        "import subprocess, tempfile\n"
        "def solve(gams_exe, mcp, tmp):\n"
        "    with tempfile.TemporaryDirectory() as pd:\n"
        "        subprocess.run([gams_exe, mcp, f'ScrDir={tmp}'], cwd=PROJECT_ROOT)\n"
    )
    fixed = leaky.replace("f'ScrDir={tmp}'", "f'ScrDir={tmp}', f'procDirPath={pd}'")
    assert scan(leaky, "x.py") == {"x.py::solve": (False, ["PROJECT_ROOT"])}
    assert scan(fixed, "x.py") == {"x.py::solve": (True, ["PROJECT_ROOT"])}


def test_documentation_is_not_an_argument() -> None:
    """PR #1760 review: a docstring naming ``procDirPath=`` made the first
    scanner report a launch that omits the option as passing."""
    src = (
        "import subprocess, tempfile\n"
        "def run(gms, scratch):\n"
        '    "Pass procDirPath={procdir} so the process dir leaves the repo."\n'
        "    # procDirPath= is set below\n"
        "    with tempfile.TemporaryDirectory() as procdir:\n"
        "        subprocess.run(['gams', gms, f'ScrDir={scratch}'])\n"
    )
    assert scan(src, "x.py") == {"x.py::run": (False, [None])}


def test_a_procdir_inside_the_checkout_does_not_count() -> None:
    """PR #1760 review: the scratch dir reused as procDirPath lived inside the
    checkout (kkt_residual's PROJECT_ROOT/output; a dir=PROJECT_ROOT temp)."""

    def src(kw: str, val: str) -> str:
        return (
            "import subprocess, tempfile\n"
            "def run(gms, scratch):\n"
            f"    with tempfile.TemporaryDirectory({kw}) as pd:\n"
            f"        subprocess.run(['gams', gms, f'procDirPath={{{val}}}'])\n"
        )

    assert scan(src("dir=PROJECT_ROOT", "pd"), "x.py")["x.py::run"][0] is False
    assert scan(src("", "scratch"), "x.py")["x.py::run"][0] is False
    assert scan(src("", "pd"), "x.py")["x.py::run"][0] is True


def test_the_argv_is_resolved_through_assigned_and_starred_lists() -> None:
    src = (
        "import subprocess, tempfile\n"
        "def starred(gams_exe, gms):\n"
        "    cmd = [gams_exe, gms]\n"
        "    with tempfile.TemporaryDirectory(prefix='p') as pd:\n"
        "        subprocess.run([*cmd, f'procDirPath={pd}'])\n"
        "def appended(gams_exe, gms):\n"
        "    cmd = [gams_exe, gms]\n"
        "    with tempfile.TemporaryDirectory() as pd:\n"
        "        cmd.append(f'procDirPath={pd}')\n"
        "        subprocess.run(cmd)\n"
        "def self_ref(gams_exe, gms):\n"
        "    cmd = [gams_exe, gms]\n"
        "    cmd = cmd + ['lo=0']\n"
        "    subprocess.run(cmd)\n"
    )
    got = scan(src, "x.py")
    assert got["x.py::starred"][0] is True
    assert got["x.py::appended"][0] is True
    assert got["x.py::self_ref"][0] is False


def test_a_mutation_after_a_launch_does_not_protect_it() -> None:
    """PR #1760 review: with every mutation in the function counted, the FIRST
    launch below was reported protected by an append that only happens later."""
    src = (
        "import subprocess, tempfile\n"
        "def two(gams_exe, gms):\n"
        "    cmd = [gams_exe, gms]\n"
        "    with tempfile.TemporaryDirectory() as pd:\n"
        "        subprocess.run(cmd)\n"
        "        cmd.append(f'procDirPath={pd}')\n"
        "        subprocess.run(cmd)\n"
        "def reassigned(gams_exe, gms):\n"
        "    with tempfile.TemporaryDirectory() as pd:\n"
        "        cmd = [gams_exe, gms, f'procDirPath={pd}']\n"
        "        cmd = [gams_exe, gms]\n"
        "        subprocess.run(cmd)\n"
    )
    got = scan(src, "x.py")
    assert got["x.py::two"][0] is False  # one launch of two is unprotected
    assert got["x.py::reassigned"][0] is False  # the last assignment wins


def test_the_launch_must_be_inside_the_tempdir_block() -> None:
    """A launch after the ``with`` closes names a directory that no longer exists."""
    src = (
        "import subprocess, tempfile\n"
        "def after(gams_exe, gms):\n"
        "    with tempfile.TemporaryDirectory() as pd:\n"
        "        pass\n"
        "    subprocess.run([gams_exe, gms, f'procDirPath={pd}'])\n"
    )
    assert scan(src, "x.py")["x.py::after"][0] is False


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
