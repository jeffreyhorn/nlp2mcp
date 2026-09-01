"""Fast source-level prescan: any `name(a,b,...)` whose arg list repeats a bare identifier.

Deliberately OVER-inclusive — it cannot tell a declaration from an equation
reference. Its job is to bound the IR census from the other side: if the IR
census reports a model with no repeated-symbol domain but the prescan flags a
declaration-looking line in it, that gap needs an explanation.
"""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
_os.makedirs(OUT, exist_ok=True)
import re, pathlib, collections, json

RAW = pathlib.Path("data/gamslib/raw")
CALL = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*\(([A-Za-z0-9_,\s'\".+-]*)\)")
DECL = re.compile(r"^\s*(set|sets|variable|variables|positive variable[s]?|free variable[s]?|"
                  r"parameter|parameters|table|scalar|equation|equations|alias)\b", re.I)

hits = collections.defaultdict(list)
for path in sorted(RAW.glob("*.gms")):
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    in_decl = False
    for n, raw in enumerate(lines, 1):
        line = raw.split("*", 1)[0] if raw.lstrip().startswith("*") else raw
        if DECL.match(raw): in_decl = True
        elif raw.strip().endswith(";"): pass
        if not raw.strip(): in_decl = False
        for m in CALL.finditer(line):
            args = [a.strip() for a in m.group(2).split(",")]
            bare = [a for a in args if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a or "")]
            if len(bare) >= 2 and len(bare) != len({b.lower() for b in bare}):
                hits[path.stem].append((n, m.group(0)[:60], in_decl))
        if raw.strip().endswith(";"): in_decl = False

decl_models = {k: [h for h in v if h[2]] for k, v in hits.items()}
decl_models = {k: v for k, v in decl_models.items() if v}
print(f"models with ANY repeated-identifier paren list: {len(hits)}")
print(f"models where at least one is on a DECLARATION line: {len(decl_models)}\n")
for k in sorted(decl_models):
    seen=set(); items=[]
    for n,txt,_ in decl_models[k]:
        key=txt.split("(")[0].strip().lower()
        if key in seen: continue
        seen.add(key); items.append(f"L{n} {txt}")
    print(f"  {k}: {'; '.join(items[:4])}")
pathlib.Path(f"{OUT}/prescan.json").write_text(json.dumps({k:[[n,t] for n,t,d in v] for k,v in decl_models.items()}, indent=1))
