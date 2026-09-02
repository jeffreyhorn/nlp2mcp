"""Corpus IR scan for CGE structure and Walras-degeneracy signals (Unknowns 9.1, 9.2).

ANALYSIS ONLY over the IR. No model is solved; no camcge experiment is run.

Signals recorded per model:
  price_vars      variables whose name looks like a price (p, pq, pd, pw, py, pk, pm, cpi...)
  fixed_prices    price variables carrying a .fx (an explicit numeraire declaration)
  clearing_eqs    equations whose name looks like market clearing (equil, mkt, clear, bal...)
  balance_eqs     equations that look like an income/budget/Walras balance
  sam_params      parameters that look like a SAM (sam, sam0, z, ...) and their domains
"""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t10")
_os.makedirs(OUT, exist_ok=True)

import json, re, signal, sys, pathlib
sys.setrecursionlimit(50000); sys.path.insert(0, ".")
from src.ir.parser import parse_model_file

PRICE = re.compile(r"^(p|pr|price|cpi|pindex|pi)([a-z0-9_]*)$", re.I)
CLEAR = re.compile(r"(equil|mkt|market|clear|supply|demand|bal)", re.I)
BALANCE = re.compile(r"(walras|income|budget|gdp|sav|invbal|lmequil|hhinc|yinc)", re.I)
SAM = re.compile(r"^(sam|sam0|z|zz|io|iomat|social)", re.I)

RAW = pathlib.Path("data/gamslib/raw")
class TO(Exception): pass
def bail(*a): raise TO

out = {}
models = sorted(RAW.glob("*.gms"))
print(f"{len(models)} models", flush=True)
for i, path in enumerate(models, 1):
    name = path.stem
    rec = {"parsed": False}
    signal.signal(signal.SIGALRM, bail); signal.alarm(120)
    try:
        m = parse_model_file(str(path))
        rec["parsed"] = True
        pv = [v for v in m.variables if PRICE.match(v)]
        # a price is "fixed" if the model declares an .fx on it
        fixed = []
        for v in pv:
            vd = m.variables[v]
            fx = getattr(vd, "fx_map", None) or getattr(vd, "fx", None)
            if fx: fixed.append(v)
        rec["price_vars"] = sorted(pv)
        rec["fixed_prices"] = sorted(fixed)
        rec["clearing_eqs"] = sorted(e for e in m.equations if CLEAR.search(e))
        rec["balance_eqs"] = sorted(e for e in m.equations if BALANCE.search(e))
        rec["sam_params"] = {p: list(getattr(m.params[p], "domain", ()) or ()) 
                             for p in m.params if SAM.match(p)}
        rec["n_eq"] = len(m.equations); rec["n_var"] = len(m.variables)
    except TO:
        rec["error"] = "TIMEOUT 120s"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:160]
    finally:
        signal.alarm(0)
    out[name] = rec
    if i % 25 == 0: print(f"  ...{i}/{len(models)}", flush=True)

pathlib.Path(f"{OUT}/cge_scan.json").write_text(json.dumps(out, indent=1))
print("DONE", flush=True)
