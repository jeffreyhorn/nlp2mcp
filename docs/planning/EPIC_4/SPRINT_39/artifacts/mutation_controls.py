"""The two mutation controls behind the survey's strongest claim (Unknown 5.3).

A green property test is not evidence. These reproduce the two controls:

  P1  Disable ``dedupe_repeated_variable_domains`` (Issue #1062) and re-emit
      tricp. P1 must FIRE — otherwise it is only passing because the guard
      makes it vacuous.
  P2  Compare elec's golden before and after the Sprint-38 Day-12 fix
      (``82b91c94``). P2 must fire on the pre-fix emit and not on today's.

Run from the repo root.  Writes into ``$OUT`` (default ``/tmp/s39t7``).
"""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")

import pathlib
import re
import subprocess
import sys

sys.setrecursionlimit(50000)
sys.path.insert(0, ".")

HEAD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*(?:\$[^.]*)?\.\.", re.M)
GUARD = re.compile(r"\$\(")
#: Any symbol call. The repeat test runs over its bare-identifier arguments,
#: so it catches EVERY arity and position -- `p(x,x)`, `p(x,y,x)`, `p(x,x,z)`.
#: The earlier `name(x,x)` regex only caught the binary ADJACENT form and
#: missed nonsharp's `inter(col,col,stm)` entirely (PR #1718 review).
CALL = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\(([^()]*)\)")
BARE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def repeats(fragment: str) -> list[str]:
    """Symbol calls in ``fragment`` whose bare-identifier arguments repeat.

    Case-INSENSITIVE, because GAMS identifiers are: `p(I,i)` is a repeat.
    """
    out = []
    for m in CALL.finditer(fragment):
        args = [a.strip() for a in m.group(2).split(",")]
        bare = [a for a in args if BARE.fullmatch(a or "")]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(m.group(0))
    return out


def p1(txt: str) -> list[str]:
    out = []
    for m in HEAD.finditer(txt):
        bare = [a.strip() for a in m.group(2).split(",")
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a.strip())]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(f"{m.group(1)}({m.group(2)})")
    return sorted(set(out))


def p2(txt: str) -> list[str]:
    """Repeated-ARGUMENT reference inside a ``$(...)`` guard.

    Deliberately NOT set-specific: the matcher is ``name(x,x)`` for any symbol,
    because the live hits are parameters and sets alike (``ts2``, ``tranc``,
    ``vs``, ``covar``). Calling it a "set" check would misdescribe it.

    Scoped to guard CONTENT on purpose: a whole-file form also matches the
    emitted ``Set ut(i,i)`` DECLARATION, which is legitimate and present in elec
    both before and after the fix -- a false positive that would get the check
    deleted.

    KNOWN GAP (PR #1718 review): it does not inspect an assignment's LEFT-HAND
    SIDE. gussrisk's ``covar(stocks,stocks)$(NOT ...) = 0;`` is caught only
    because the repeat ALSO appears inside the guard; a repeated LHS with a
    clean guard would be missed. The line filter (``".." in line or "=" in
    line``) selects candidate lines, it does not widen what is scanned.
    """
    out = []
    for line in txt.split("\n"):
        if ".." not in line and "=" not in line:
            continue
        for gm in GUARD.finditer(line):
            depth, i = 1, gm.end()
            while i < len(line) and depth:
                depth += (line[i] == "(") - (line[i] == ")")
                i += 1
            out += repeats(line[gm.end():i])
    return sorted(set(out))


#: The Sprint-38 Day-12 commit that fixed elec. Its PARENT holds the pre-fix
#: golden, which is the P2 control's fail-before.
ELEC_FIX = "82b91c94"


def _elec_prefix_golden() -> str | None:
    """The pre-fix elec golden, or None with an actionable message.

    `git show <sha>^:<path>` is unavailable in a shallow clone (CI checkouts
    default to depth 1) and in an archive export. Failing there with a raw
    CalledProcessError would contradict this directory's "reproducible from the
    repo" claim, so say what to do about it instead. (PR #1718 review.)
    """
    r = subprocess.run(
        ["git", "show", f"{ELEC_FIX}^:data/gamslib/mcp/elec_mcp.gms"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        return r.stdout
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"], capture_output=True, text=True
    ).stdout.strip()
    print(f"P2 control -- CANNOT RUN: `git show {ELEC_FIX}^:...` failed")
    print(f"    git said: {r.stderr.strip().splitlines()[0] if r.stderr.strip() else '(no stderr)'}")
    if shallow == "true":
        print("    Cause: this is a SHALLOW clone, so the pre-fix commit is absent.")
        print("    Fix:   git fetch --unshallow      (CI: actions/checkout with fetch-depth: 0)")
    else:
        print(f"    Cause: commit {ELEC_FIX} is not in this repository's history.")
        print("    Fix:   fetch the branch containing it, or run from a full clone of the upstream repo.")
    print("    The P1 control above does not need git history and its result stands.")
    return None


def main() -> int:
    outdir = pathlib.Path(OUT)
    outdir.mkdir(parents=True, exist_ok=True)
    failures = []

    # --- P1 control: #1062 disabled, tricp must violate --------------------
    import src.cli as cli
    cli.dedupe_repeated_variable_domains = lambda m: {}          # the mutation
    mutant = outdir / "tricp_nodedupe.gms"
    try:
        cli.main(args=["data/gamslib/raw/tricp.gms", "-o", str(mutant),
                       "--skip-convexity-check"], standalone_mode=False)
    except SystemExit:
        pass
    hits = p1(mutant.read_text())
    print(f"P1 control -- tricp with #1062 disabled : {len(hits)} violation(s) {hits}")
    if not hits:
        failures.append("P1 did not fire on the mutant: the property is vacuous")

    # --- P1 must NOT fire on the corpus as it stands ------------------------
    live = sorted(pathlib.Path("data/gamslib/mcp").glob("*.gms"))
    heads = sum(len(HEAD.findall(f.read_text(errors="replace"))) for f in live)
    v1 = {f.stem: p1(f.read_text(errors="replace")) for f in live}
    n1 = sum(len(v) for v in v1.values())
    print(f"P1 live    -- {len(live)} goldens, {heads} heads : {n1} violation(s)")
    if n1:
        failures.append(f"P1 fires on the committed corpus: {[k for k,v in v1.items() if v]}")

    # --- P2 control: elec before vs after 82b91c94 --------------------------
    pre = outdir / "elec_prefix.gms"
    text = _elec_prefix_golden()
    if text is None:
        failures.append(
            "P2 control could not run: the pre-fix elec golden is unreachable"
        )
    else:
        pre.write_text(text)
    if text is not None:
        before = p2(pre.read_text())
        after = p2(pathlib.Path("data/gamslib/mcp/elec_mcp.gms").read_text())
        print(f"P2 control -- elec pre-fix {len(before)} {before} / today {len(after)}")
        if not before:
            failures.append("P2 did not fire on elec pre-fix: the property is vacuous")
        if after:
            failures.append("P2 fires on elec today: the property has a false positive")

    for f in failures:
        print(f"  FAIL: {f}")
    print("ALL CONTROLS PASS" if not failures else f"{len(failures)} CONTROL(S) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
