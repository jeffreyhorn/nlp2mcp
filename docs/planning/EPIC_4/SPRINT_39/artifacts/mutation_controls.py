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
REPEAT = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\(\s*([A-Za-z][A-Za-z0-9_]*)\s*,\s*\2\s*\)")


def p1(txt: str) -> list[str]:
    out = []
    for m in HEAD.finditer(txt):
        bare = [a.strip() for a in m.group(2).split(",")
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a.strip())]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(f"{m.group(1)}({m.group(2)})")
    return sorted(set(out))


def p2(txt: str) -> list[str]:
    """Repeated-symbol reference inside a ``$(...)`` guard or an assignment.

    Scoped deliberately: a whole-file form also matches the emitted ``Set
    ut(i,i)`` DECLARATION, which is legitimate and present in elec both before
    and after the fix -- a false positive that would get the check deleted.
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
            out += [m.group(0) for m in REPEAT.finditer(line[gm.end():i])]
    return sorted(set(out))


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
    pre.write_text(subprocess.run(
        ["git", "show", "82b91c94^:data/gamslib/mcp/elec_mcp.gms"],
        capture_output=True, text=True, check=True).stdout)
    before, after = p2(pre.read_text()), p2((pathlib.Path("data/gamslib/mcp/elec_mcp.gms")).read_text())
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
