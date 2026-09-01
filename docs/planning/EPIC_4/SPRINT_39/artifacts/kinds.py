"""Per-kind IR confirmation for the 34 prescan candidates."""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
_os.makedirs(OUT, exist_ok=True)
import json, sys, signal, pathlib
sys.setrecursionlimit(50000); sys.path.insert(0, ".")
from src.ir.parser import parse_model_file
cands = sorted(json.load(open(f"{OUT}/prescan.json")))
out={}
class TO(Exception): pass
def bail(*a): raise TO
for i,name in enumerate(cands,1):
    rec={}
    signal.signal(signal.SIGALRM,bail); signal.alarm(150)
    try:
        m=parse_model_file(f"data/gamslib/raw/{name}.gms")
        for kind,tab in (("sets",m.sets),("variables",m.variables),("params",m.params),("equations",m.equations)):
            rep={s:list(getattr(d,"domain",()) or ()) for s,d in tab.items()
                 if (lambda dd: len(dd)!=len({x.lower() for x in dd}))(tuple(getattr(d,"domain",()) or ()))}
            if rep: rec[kind]=rep
    except TO: rec["error"]="TIMEOUT 150s"
    except Exception as e: rec["error"]=f"{type(e).__name__}: {e}"[:120]
    out[name]=rec
    print(f"{i:3d}/{len(cands)} {name}: {rec if rec else 'none'}", flush=True)
pathlib.Path(f"{OUT}/kinds.json").write_text(json.dumps(out,indent=1))
print("DONE")
