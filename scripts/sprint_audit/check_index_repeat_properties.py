#!/usr/bin/env python3
"""P1 + P2 — repeated-index properties over the committed goldens.

Sprint 39 P10, graduating Prep Task 7's `artifacts/property2.py` into a gate.

**P1 — no emitted equation HEAD repeats a controlling index symbol.**
Measured 0 violations across 3,100 heads in 193 goldens, so this is a HARD
gate: any violation fails. A repeated controlling index in an emitted head
leaves the MCP with unmatched columns; there is no legitimate instance.

**P2 — no emitted ``$(...)`` guard references a symbol at a repeated index.**
Measured **9 violations across 6 goldens today**, all of them real findings
(see `SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` §P2). So P2 is a RATCHET, not a
hard gate: violations must stay within the recorded baseline, any NEW one
fails, and fixing one requires removing its baseline entry.

⚠ WHY A BASELINE RATHER THAN A HARD GATE. Nine violations sit in committed
goldens right now. A gate that goes red on untouched history gets switched
off, and a switched-off gate protects nothing -- the same reasoning that made
the Phase-0 8a/8b requirements added-only (CONTRIBUTING §*Close-Rule
Preconditions and Carried-Package Evidence*).

⚠ WHY P2 SCANS GUARD CONTENT ONLY, AND WHY THE "KNOWN GAP" IS NOT CLOSED.
The survey records a gap -- P2 does not inspect an assignment's left-hand
side -- and recommends closing it as "a one-line extension" when P2 graduates.
**Measured before implementing, that extension is 8/8 false positives:**

    china     crec(cf,cf)$(not sum(ca, crec(ca,cf))) = 1;   verbatim in source
    prolog    eta(g,g,h) = ...                              verbatim in source
    markov    pi(s,i,sp,j,sp) = pr(i,j);                    verbatim in source
    orani     ce(c,c) = 1;  /  etabar(c,s,c,s)              verbatim in source
    dinam     a(id,id,te)                                   verbatim in source
    egypt     yld(c,c,r) = yield(c,r);                      verbatim in source
    danwolfe  e(i,i) = 0;                                   deliberate diagonal

Every hit is a **source-faithful diagonal assignment** -- ordinary GAMS the
emitter reproduced correctly. Adding them would give the check 8 false
positives against 9 true findings, and a check at that rate gets deleted:
exactly the outcome the survey itself predicts for the `Set ut(i,i)`
declaration class. **The guard-content scoping is load-bearing, not a
limitation.** The gap is real but narrower than "inspect the LHS": it would
need to distinguish a *manufactured* repeat from a *source-faithful* one,
which the emitted text alone does not carry.

Run from the repo root. Exits non-zero if P1 has any violation, or if P2 has a
violation outside the baseline.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MCP = ROOT / "data/gamslib/mcp"
BASELINE = ROOT / "scripts/sprint_audit/index_repeat_p2_baseline.json"

#: An emitted equation head: ``name(args) [$cond] ..``
HEAD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*(?:\$[^.]*)?\.\.", re.M)
GUARD = re.compile(r"\$\(")
#: Any symbol call. The repeat test runs over its bare-identifier arguments, so
#: it catches every arity and position -- ``p(x,x)``, ``p(x,y,x)``, ``p(x,x,z)``.
#: An earlier ``name(x,x)`` form caught only the binary ADJACENT case and missed
#: nonsharp's ``inter(col,col,stm)`` entirely (Prep Task 7, PR #1718 review).
CALL = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\(([^()]*)\)")
BARE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def repeats(fragment: str) -> list[str]:
    """Symbol calls in *fragment* whose bare-identifier arguments repeat.

    Case-INSENSITIVE, because GAMS identifiers are: ``p(I,i)`` is a repeat.
    """
    out = []
    for m in CALL.finditer(fragment):
        args = [a.strip() for a in m.group(2).split(",")]
        bare = [a for a in args if BARE.fullmatch(a or "")]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(m.group(0))
    return out


def p1_violations(text: str) -> list[str]:
    """Equation heads whose controlling index symbols repeat."""
    out = []
    for m in HEAD.finditer(text):
        bare = [a.strip() for a in m.group(2).split(",") if BARE.fullmatch(a.strip() or "")]
        if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
            out.append(f"{m.group(1)}({m.group(2)})")
    return sorted(set(out))


def p2_violations(text: str) -> list[str]:
    """Repeated-argument references inside ``$(...)`` guard CONTENT.

    Scoped to guard content deliberately -- see the module docstring. A
    whole-file form also matches the emitted ``Set ut(i,i)`` declaration, which
    is legitimate and present in elec both before and after its fix.
    """
    out: list[str] = []
    for line in text.split("\n"):
        if ".." not in line and "=" not in line:
            continue
        for gm in GUARD.finditer(line):
            depth, i = 1, gm.end()
            while i < len(line) and depth:
                depth += (line[i] == "(") - (line[i] == ")")
                i += 1
            out += repeats(line[gm.end() : i])
    return sorted(set(out))


def scan(mcp_dir: pathlib.Path) -> tuple[dict[str, list[str]], dict[str, list[str]], int, int]:
    """Return (p1 by model, p2 by model, goldens scanned, heads seen)."""
    p1: dict[str, list[str]] = {}
    p2: dict[str, list[str]] = {}
    goldens = sorted(mcp_dir.glob("*.gms"))
    heads = 0
    for g in goldens:
        text = g.read_text(encoding="utf-8")
        heads += len(HEAD.findall(text))
        if v := p1_violations(text):
            p1[g.stem] = v
        if v := p2_violations(text):
            p2[g.stem] = v
    return p1, p2, len(goldens), heads


def main() -> int:
    ap = argparse.ArgumentParser(description="P1/P2 repeated-index gate.")
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="rewrite the P2 baseline from the current corpus (use when FIXING a violation)",
    )
    args = ap.parse_args()

    if not MCP.is_dir():
        print(f"ERROR: {MCP} not found — nothing scanned", file=sys.stderr)
        return 2

    p1, p2, n_goldens, n_heads = scan(MCP)
    print(f"Index-repeat properties: {n_goldens} golden(s), {n_heads} equation head(s).")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(p2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        total = sum(len(v) for v in p2.values())
        print(f"  baseline rewritten: {total} P2 violation(s) across {len(p2)} model(s)")
        return 0

    fail = False

    # --- P1: hard gate -----------------------------------------------------
    if p1:
        fail = True
        total = sum(len(v) for v in p1.values())
        print(f"  P1 FAIL: {total} violation(s) across {len(p1)} model(s)")
        for model, vs in sorted(p1.items()):
            print(f"    {model}: {', '.join(vs)}")
        print(
            "\n  An emitted equation head must not repeat a controlling index symbol:\n"
            "  the MCP is then left with unmatched columns. There is no legitimate\n"
            "  instance — 0 violations across 3,100 heads when this gate landed."
        )
    else:
        print(f"  P1 OK: 0 violation(s) in {n_heads} head(s)")

    # --- P2: ratchet against the baseline ----------------------------------
    base: dict[str, list[str]] = {}
    if BASELINE.is_file():
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
    else:
        print(f"  P2 WARN: no baseline at {BASELINE.relative_to(ROOT)} — treating as empty")

    new = {m: sorted(set(v) - set(base.get(m, []))) for m, v in p2.items()}
    new = {m: v for m, v in new.items() if v}
    fixed = {m: sorted(set(v) - set(p2.get(m, []))) for m, v in base.items()}
    fixed = {m: v for m, v in fixed.items() if v}

    total_p2 = sum(len(v) for v in p2.values())
    total_base = sum(len(v) for v in base.values())
    print(f"  P2: {total_p2} violation(s) across {len(p2)} model(s); baseline {total_base}")

    if new:
        fail = True
        print(f"  P2 FAIL: {sum(len(v) for v in new.values())} NEW violation(s) not in the baseline")
        for model, vs in sorted(new.items()):
            print(f"    {model}: {', '.join(vs)}")
        print(
            "\n  A repeated index inside an emitted `$(...)` guard is manufactured\n"
            "  unless the source declares it so. It silently makes the guard\n"
            "  identically true or identically false — see\n"
            "  docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md §P2."
        )

    if fixed:
        # Not a failure — but the baseline must shrink, or the ratchet slips.
        print(f"  P2 RATCHET: {sum(len(v) for v in fixed.values())} baseline entry/entries no longer present")
        for model, vs in sorted(fixed.items()):
            print(f"    {model}: {', '.join(vs)} — remove from the baseline (`--update-baseline`)")

    print("\n" + ("FAIL" if fail else "PASS"))
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
