"""Blast radius by LINE TRACING — which primary sites actually execute, per model.

sys.settrace rather than source instrumentation: nothing is written into src/,
so there is no instrumented file to forget to restore.
"""
import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
import sys, json, signal, collections, pathlib
sys.setrecursionlimit(50000); sys.path.insert(0, ".")

SITES = {
 ("src/ad/constraint_jacobian.py",1466):"K4 _sub_idx",
 ("src/ad/constraint_jacobian.py",1474):"K4 _sub_idx IndexOffset",
 ("src/ad/constraint_jacobian.py",1513):"K4 _substitute_indices Sum/Prod",
 ("src/ad/constraint_jacobian.py",1536):"K4 _substitute_indices SymbolRef",
 ("src/ad/derivative_rules.py",2362):"K5 _diff_sum wrt scan",
 ("src/ad/derivative_rules.py",2411):"K5 _diff_sum duplicate_sym guard",
 ("src/emit/emit_gams.py",795):"K5 _visit domain scan",
 ("src/ir/condition_eval.py",52):"K4 star-domain split",
 ("src/ir/condition_eval.py",117):"K2 dict(zip(domain_sets,...))",
 ("src/ir/parser.py",5530):"K5 param.domain[pos] alias expand",
 ("src/ir/parser.py",6007):"K5 multidim set alias substitution",
 ("src/ir/parser.py",6086):"K4 expanded_indices.index()",
 ("src/kkt/empty_equation_detector.py",127):"K2 dict(zip(eq_def.domain,...))",
 ("src/kkt/stationarity.py",1091):"K5 _pos first-match",
 ("src/kkt/stationarity.py",1104):"K3 bindings[eqi]=p",
 ("src/kkt/stationarity.py",1500):"K5 _remap_condition_to_domain (#1350)",
 ("src/kkt/stationarity.py",3432):"K5 _apply_alias_offset_to_deriv",
 ("src/kkt/stationarity.py",4880):"K5 _match_subset_domain",
 ("src/kkt/stationarity.py",5140):"K3 _compute_index_offset_key p1",
 ("src/kkt/stationarity.py",5148):"K3 _compute_index_offset_key p2",
 ("src/kkt/stationarity.py",5770):"K5 _sigma_sp_domain_collision",
}
ROOT = str(pathlib.Path.cwd())
WANT = {(ROOT + "/" + f, l) for f, l in SITES}
FILES = {ROOT + "/" + f for f, _ in SITES}

hit = set()
def tr(frame, event, arg):
    fn = frame.f_code.co_filename
    if fn not in FILES: return None
    return trl
def trl(frame, event, arg):
    if event == "line":
        k = (frame.f_code.co_filename, frame.f_lineno)
        if k in WANT: hit.add(k)
    return trl

models = sys.argv[1:]
out = {}
import src.cli as cli
class TO(Exception): pass
def bail(*a): raise TO
for name in models:
    hit = set()
    signal.signal(signal.SIGALRM, bail); signal.alarm(240)
    sys.settrace(tr)
    try:
        cli.main(args=[f"data/gamslib/raw/{name}.gms", "-o", f"{OUT}/reach_{name}.gms",
                       "--skip-convexity-check"], standalone_mode=False)
        status = "ok"
    except TO: status = "timeout"
    except SystemExit: status = "ok"
    except Exception as e: status = f"{type(e).__name__}"
    finally:
        sys.settrace(None); signal.alarm(0)
    out[name] = {"status": status,
                 "sites": sorted(SITES[(f[len(ROOT)+1:], l)] for f, l in hit)}
    print(f"{name:10s} {status:10s} {len(hit):2d}/{len(SITES)} sites", flush=True)

pathlib.Path(f"{OUT}/reach.json").write_text(json.dumps(out, indent=1))
cnt = collections.Counter()
for v in out.values(): cnt.update(v["sites"])
print("\n=== site reach across this sample ===")
for s in sorted(SITES.values()):
    print(f"  {cnt.get(s,0):2d}/{len(models)}  {s}")
