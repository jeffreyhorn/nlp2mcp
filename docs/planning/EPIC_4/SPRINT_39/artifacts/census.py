"""Corpus census: declarations whose DOMAIN repeats a symbol, by symbol kind.

Repeated-symbol domains are counted separately for sets, variables, parameters
and equations, because the two known defects sat in different kinds (tricp: a
VARIABLE domain; elec: a SET domain) and reached different code paths.
"""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
import json, sys, signal, pathlib
sys.setrecursionlimit(50000)
sys.path.insert(0, ".")
from src.ir.parser import parse_model_file

RAW = pathlib.Path("data/gamslib/raw")
out = {}
models = sorted(RAW.glob("*.gms"))
print(f"{len(models)} models", flush=True)

class TO(Exception): pass
def bail(*a): raise TO

for i, path in enumerate(models, 1):
    name = path.stem
    rec = {"parsed": False}
    signal.signal(signal.SIGALRM, bail); signal.alarm(120)
    try:
        m = parse_model_file(str(path))
        rec["parsed"] = True
        for kind, table in (("sets", m.sets), ("variables", m.variables),
                            ("params", m.params), ("equations", m.equations)):
            rep = {}
            for sym, d in table.items():
                dom = tuple(getattr(d, "domain", ()) or ())
                if len(dom) != len(set(dom)):
                    rep[sym] = list(dom)
            rec[kind] = rep
    except TO:
        rec["error"] = "TIMEOUT 120s"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:200]
    finally:
        signal.alarm(0)
    out[name] = rec
    if i % 25 == 0: print(f"  ...{i}/{len(models)}", flush=True)

pathlib.Path(f"{OUT}/census.json").write_text(json.dumps(out, indent=1))
print("DONE", flush=True)
