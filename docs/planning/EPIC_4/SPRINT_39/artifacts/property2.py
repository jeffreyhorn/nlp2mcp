"""P1 + P2 evaluated over every committed golden, each with a mutation control."""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
_os.makedirs(OUT, exist_ok=True)
import re, pathlib, collections, time, sys

MCP = pathlib.Path("data/gamslib/mcp")
HEAD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*(?:\$[^.]*)?\.\.", re.M)
GUARD = re.compile(r"\$\(")
REPEAT = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\(\s*([A-Za-z][A-Za-z0-9_]*)\s*,\s*\2\s*\)")

def p1(txt):
    out = []
    for m in HEAD.finditer(txt):
        bare = [a.strip() for a in m.group(2).split(",")
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a.strip())]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(f"{m.group(1)}({m.group(2)})")
    return out

def p2(txt):
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
            out += [m.group(0) for m in REPEAT.finditer(line[gm.end():i])]
    return sorted(set(out))

t0 = time.time()
files = sorted(MCP.glob("*.gms"))
v1 = {f.stem: p1(f.read_text(errors="replace")) for f in files}
v2 = {f.stem: p2(f.read_text(errors="replace")) for f in files}
el = time.time() - t0
print(f"goldens        : {len(files)}   wall-clock {el:.2f}s")
print(f"P1 violations  : {sum(len(v) for v in v1.values())} in {sum(1 for v in v1.values() if v)} model(s)")
print(f"P2 violations  : {sum(len(v) for v in v2.values())} in {sum(1 for v in v2.values() if v)} model(s)")
for k,v in v2.items():
    if v: print(f"    P2 {k}: {v}")
for k,v in v1.items():
    if v: print(f"    P1 {k}: {v}")

print("\n--- MUTATION CONTROLS ---")
pre = pathlib.Path(f"{OUT}/elec_prefix.gms").read_text()
print(f"elec PRE-FIX  : P1={len(p1(pre))}  P2={len(p2(pre))} -> {p2(pre)}")
cur = (MCP / "elec_mcp.gms").read_text()
print(f"elec TODAY    : P1={len(p1(cur))}  P2={len(p2(cur))}")
mut = pathlib.Path(f"{OUT}/tricp_nodedupe.gms").read_text()
print(f"tricp MUTANT  : P1={len(p1(mut))} -> {sorted(set(p1(mut)))}  P2={len(p2(mut))}")
