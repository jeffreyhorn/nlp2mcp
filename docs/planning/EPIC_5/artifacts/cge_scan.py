"""Corpus IR scan for CGE structure and Walras-degeneracy signals (Unknowns 9.1, 9.2).

ANALYSIS ONLY over the IR. No model is solved; no camcge experiment is run.

Signals recorded per model:
  price_vars           variables whose name looks like a price (p, pd, pm, py, pk, cpi...)
  fixed_prices         price variables carrying a .fx, by the CORRECT four-field probe
  fixed_prices_fx_only price variables found by the INCOMPLETE fx/fx_map probe
  clearing_eqs         equations whose name looks like market clearing (equil, mkt, clear...)
  balance_eqs          equations that look like an income/budget/Walras balance
  sam_params           parameters that look like a SAM (sam, sam0, io, z...) and their domains

⚠ WHY TWO FIXED-PRICE FIELDS. A GAMS ``pwm.fx(i) = pwm0(i)`` does **not** land in
``VariableDef.fx`` or ``.fx_map`` — it lands in ``fx_expr_map``, because the
right-hand side is an expression. The first version of this script probed only
the first two, so **camcge read as having no fixed price when it has one**, and
the D4 detector appeared to flag it correctly (see ../CGE_DEGENERACY_SCOPING.md
§7.2). Both fields are emitted so the published table is reproducible from this
script AND the trap stays visible in its output rather than only in prose.
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
        # CORRECT: an .fx can land in any of four fields. `fx`/`fx_map` hold a
        # constant fix; `fx_expr`/`fx_expr_map` hold an expression-valued one,
        # which is the form `pwm.fx(i) = pwm0(i)` takes.
        fixed, fixed_legacy = [], []
        for v in pv:
            vd = m.variables[v]
            if vd.fx is not None or vd.fx_map or vd.fx_expr is not None or vd.fx_expr_map:
                fixed.append(v)
            # The incomplete probe, kept so the trap is visible in the output.
            # ⚠ `vd.fx is not None`, NOT `if vd.fx` — a scalar fix to 0.0 is
            # falsey, and the original probe dropped it. That is a SECOND,
            # unrelated defect; leaving it in would make this field disagree
            # with `fixed_prices` for two different reasons at once and muddy
            # the evidence. The two probes must differ in EXACTLY ONE
            # dimension — the field set — or the comparison proves nothing.
            if vd.fx is not None or vd.fx_map:
                fixed_legacy.append(v)
        rec["price_vars"] = sorted(pv)
        rec["fixed_prices"] = sorted(fixed)
        rec["fixed_prices_fx_only"] = sorted(fixed_legacy)
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
