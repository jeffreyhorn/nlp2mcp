# sarf profiling harness — Sprint 40 Prep Task 9 (scratch; never committed as code)

These scripts produced every figure in `../SARF_JACOBIAN_DESIGN.md`. They lived **outside the repo** (`/tmp/t9/`) and were run from the repo root with `.venv/bin/python <script> …`. They are reproduced here as text, so the PR adds **no `*.py`**. **None modifies `src/` on disk.** All patching is in-process, at the point of use.

| script | produced |
|---|---|
| `prof.py` | §1 Run A (`cProfile`, two windows) and the sleep positive control |
| `phases.py` | §1 Run B (unprofiled phase timing, `differentiate_expr` per Jacobian path) |
| `fixture.py` | §6 declared-cardinality sweep (fail-before) and the golden hashes |
| `proto.py` | §3 the in-memory E1 filter prototype (fixture byte-identity, the sarf phases, the `RecursionError` traceback with `T9_VVV=1`) |
| `cov_one.sh` | §5 per-model coverage of `src/ad/gradient.py` (run via `xargs -P 4`) |

⚠ **`proto.py`'s first version had an indentation bug** (12- vs 16-space anchor). It moved the inserted filter out of the per-variable loop and **silently dropped the `cap(i)` constraint** from the fixture's emit. The fixture's byte-identity golden caught it. The version below is the corrected one.

⚠ **A second prototype bug, found in review (PR #1754):** the position-map cache used `_T9_POS.setdefault(var_name, {…comprehension…})`. That evaluates the comprehension on **every** call, a cache hit included, so it rebuilt the full declared-position map **per row**: O(declared) per row, the Day-7 trap. The version below builds each map **only on a cache miss** and **counts the builds** (`position_map_builds` in its JSON output). It also patches **E2** (`_compute_bound_jacobian`), and `fixture.py` now carries an `.fx` bound so E2 is actually exercised.

⚠ **A third harness bug, found in review (PR #1754):** `Stop` (the cap exception) subclassed `Exception`. `src/cli.py` (~L756–762) catches `Exception` and calls `sys.exit(1)`, so a cap that fired **during** the translate was recorded as `systemexit 1` / `SystemExit: 1`, indistinguishable from a real failure. **All three scripts now define `Stop(BaseException)`** (verified: a 5 s cap on sarf records `stopped_at_cap` in all three).
**How the runs recorded *before* this fix were read** (none of the design's conclusions rests on the `rc` field):
- **Run A** (`prof.py`, `rc: systemexit 1`) and **Run B** (`phases.py`, `rc: SystemExit: 1`) were **cap stops**: Run A's final snapshot fired at 600.07 s (wall 600.67 s) and Run B's wall is 900.0 s, each at its cap, with Run B stamping the in-flight inequality phase's exit at **900.03 s**.
- **The three `proto.py` sarf runs** (`SystemExit: 1`) were **genuine failures**: each ended well **before** its 1,200 s cap (walls 527.3, 453.7 and 428.9 s), and each run's log records `maximum recursion depth exceeded` (the `-vvv` runs with the full traceback).

## `prof.py`

```python
"""Task 9 scratch profiler (outside the repo). Time-boxed cProfile of a full
sarf translate, with snapshots at W1 and W2 seconds (two windows).

usage: python prof.py <model> <outdir> <w1> <w2> [--control]
--control wraps src.cli.parse_model_file with a 5 s sleep (positive control).
"""
import cProfile, json, os, signal, sys, time

sys.setrecursionlimit(50000)
model, outdir, W1, W2 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
control = "--control" in sys.argv
os.makedirs(outdir, exist_ok=True)
sys.path.insert(0, os.getcwd())
import src.cli as cli  # noqa: E402

events = {"t0": None, "jacobian_entered": None, "jacobian_returned": None}
_orig_jac = cli.compute_constraint_jacobian
def _jac(*a, **k):
    events["jacobian_entered"] = time.time() - events["t0"]
    r = _orig_jac(*a, **k)
    events["jacobian_returned"] = time.time() - events["t0"]
    return r
cli.compute_constraint_jacobian = _jac

if control:
    _orig_parse = cli.parse_model_file
    def t9_control_parse(*a, **k):  # deliberate 5 s sleep in a known function
        time.sleep(5.0)
        return _orig_parse(*a, **k)
    cli.parse_model_file = t9_control_parse

pr = cProfile.Profile()
class Stop(BaseException):  # NOT Exception: src/cli.py catches Exception and sys.exit(1)s, which would mask the cap
    pass
def on_alarm(signum, frame):
    pr.disable()
    el = time.time() - events["t0"]
    if not hasattr(on_alarm, "n"):
        on_alarm.n = 1
        pr.dump_stats(f"{outdir}/w1.prof"); events["w1_at"] = el
        signal.alarm(W2 - W1); pr.enable()
    else:
        pr.dump_stats(f"{outdir}/w2.prof"); events["w2_at"] = el
        raise Stop()
signal.signal(signal.SIGALRM, on_alarm)
events["t0"] = time.time(); signal.alarm(W1)
rc = "running"
pr.enable()
try:
    cli.main.main([f"data/gamslib/raw/{model}.gms", "-o", f"{outdir}/{model}_mcp.gms", "--quiet"], standalone_mode=False)
    rc = "completed"
except Stop:
    rc = "stopped_at_cap"
except SystemExit as e:
    rc = f"systemexit {e.code}"
finally:
    pr.disable()
    if rc != "stopped_at_cap":
        pr.dump_stats(f"{outdir}/final.prof")
    events["rc"] = rc; events["wall"] = time.time() - events["t0"]
    json.dump(events, open(f"{outdir}/events.json", "w"), indent=1)
    print(json.dumps(events))
```

## `phases.py`

```python
"""Task 9 scratch: UNPROFILED phase timing of a sarf translate (outside the repo).
Wall timestamps at entry/exit of each phase + differentiate_expr calls per
Jacobian path; hard cap via SIGALRM. usage: python phases.py <model> <out.json> <cap_s>
"""
import json, os, signal, sys, time
sys.setrecursionlimit(50000); sys.path.insert(0, os.getcwd())
model, out, CAP = sys.argv[1], sys.argv[2], int(sys.argv[3])
import src.cli as cli, src.ad.constraint_jacobian as cj, src.ad.gradient as gr  # noqa: E402

T0 = [None]; EV = []; CNT = {}; CTX = ["other"]
def stamp(name, kind): EV.append((round(time.time() - T0[0], 2), name, kind))
def timed(mod, attr, tag=None):
    orig = getattr(mod, attr)
    def w(*a, **k):
        stamp(attr, "enter");
        if tag: CTX.append(tag)
        try: return orig(*a, **k)
        finally:
            if tag: CTX.pop()
            stamp(attr, "exit")
    setattr(mod, attr, w)
timed(cli, "parse_model_file"); timed(cli, "compute_objective_gradient", "gradient")
timed(cli, "compute_constraint_jacobian")
for a, t in (("_compute_equality_jacobian", "equality"), ("_compute_inequality_jacobian", "inequality"), ("_compute_bound_jacobian", "bound")):
    timed(cj, a, t)
for mod in (cj, gr):
    if hasattr(mod, "differentiate_expr"):
        o = mod.differentiate_expr
        def d(*a, _o=o, **k):
            CNT[CTX[-1]] = CNT.get(CTX[-1], 0) + 1
            return _o(*a, **k)
        mod.differentiate_expr = d
class Stop(BaseException): pass  # NOT Exception: src/cli.py catches Exception and sys.exit(1)s, which would mask the cap
def alarm(*_): raise Stop()
def dump(rc):
    json.dump({"rc": rc, "cap_s": CAP, "wall": round(time.time() - T0[0], 1), "events": EV, "diff_calls": CNT}, open(out, "w"), indent=1)
signal.signal(signal.SIGALRM, alarm)
T0[0] = time.time(); signal.alarm(CAP)
try:
    cli.main.main([f"data/gamslib/raw/{model}.gms", "-o", f"/tmp/t9/{model}_phases_mcp.gms", "--quiet"], standalone_mode=False)
    dump("completed")
except Stop:
    dump("stopped_at_cap")
except BaseException as e:
    dump(f"{type(e).__name__}: {e}"[:200])
```

## `fixture.py`

```python
"""Task 9 scratch fixture sweep (outside the repo).

Declared >> active shape, active set FIXED, declared cardinality scaled:
  x(i,j), |i| = 3, |j| = N;  every row references only x(i,a), a(j) = j1*j5.
  obj   (equality,   filtered path)   z =e= sum((i,a), x(i,a))
  cap(i)(inequality, UNfiltered path) sum(a, x(i,a)) =l= 10
  x.up('i1','j1') = 5                 (an UP bound: normalize puts it in `inequalities`, so it is E1's)
  x.fx('i2','j2') = 1                 (an FX bound: Rel.EQ, in `equalities`, so _compute_bound_jacobian -- E2 -- processes it)

usage: python fixture.py <outdir> N [N ...]
Prints one JSON line per N: translate seconds, differentiate_expr calls per
Jacobian path, and the sha256 of the emitted MCP.
"""
import hashlib, json, os, sys, time

sys.setrecursionlimit(50000)
sys.path.insert(0, os.getcwd())
outdir = sys.argv[1]; sizes = [int(x) for x in sys.argv[2:]]
os.makedirs(outdir, exist_ok=True)

import src.ad.constraint_jacobian as cj  # noqa: E402
import src.cli as cli  # noqa: E402

COUNTS = {}
_ctx = ["other"]
_orig_diff = cj.differentiate_expr
def _diff(*a, **k):
    COUNTS[_ctx[-1]] = COUNTS.get(_ctx[-1], 0) + 1
    return _orig_diff(*a, **k)
cj.differentiate_expr = _diff
for name, tag in (("_compute_equality_jacobian", "equality"),
                  ("_compute_inequality_jacobian", "inequality"),
                  ("_compute_bound_jacobian", "bound")):
    orig = getattr(cj, name)
    def wrap(*a, _o=orig, _t=tag, **k):
        _ctx.append(_t)
        try:
            return _o(*a, **k)
        finally:
            _ctx.pop()
    setattr(cj, name, wrap)

GMS = """Set i / i1*i3 /, j / j1*j{N} /, a(j) / j1*j5 /;
Variable z;
Positive Variable x(i,j);
x.up('i1','j1') = 5;
x.fx('i2','j2') = 1;
Equation obj, cap(i);
obj..    z =e= sum((i,a), x(i,a));
cap(i).. sum(a, x(i,a)) =l= 10;
Model m / all /;
solve m using lp minimizing z;
"""
for N in sizes:
    src = f"{outdir}/declfix_{N}.gms"; out = f"{outdir}/declfix_{N}_mcp.gms"
    open(src, "w").write(GMS.format(N=N))
    COUNTS.clear()
    t = time.perf_counter()
    try:
        cli.main.main([src, "-o", out, "--quiet"], standalone_mode=False)
        rc = "ok"
    except SystemExit as e:
        rc = f"exit {e.code}"
    el = time.perf_counter() - t
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest() if os.path.exists(out) else None
    print(json.dumps({"N": N, "declared_x": 3 * N, "active_x": 15, "rc": rc, "translate_s": round(el, 3),
                      "diff_calls": dict(sorted(COUNTS.items())), "diff_total": sum(COUNTS.values()),
                      "emit_sha256": sha, "emit_bytes": os.path.getsize(out) if os.path.exists(out) else None}),
          flush=True)
```

## `proto.py`

```python
"""Task 9 scratch PROTOTYPE (outside the repo, in memory only, never landed).

Rebuilds `_compute_inequality_jacobian` from its OWN source with the equality
path's Sprint-38 referenced-tuple filter inserted (same sort-by-declared-position
construction), then runs a translate. `src/` on disk is untouched.

usage: python proto.py <gms> <out_mcp> <cap_s> <phases.json>
"""
import inspect, json, os, signal, sys, textwrap, time
sys.setrecursionlimit(50000); sys.path.insert(0, os.getcwd())
gms, out, CAP, pj = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
import src.ad.constraint_jacobian as cj, src.cli as cli  # noqa: E402

def _filtered_source(fn, indent, expr_name):
    src = textwrap.dedent(inspect.getsource(fn))
    I = " " * indent
    OLD = I + "for var_indices in var_instances:\n"
    assert src.count(OLD) == 1, (fn.__name__, src.count(OLD))
    NEW = (I + f"_ref = _referenced_index_tuples({expr_name}, var_name, model_ir)\n"
           + I + "if _ref is None:\n"
           + I + "    _eff = var_instances\n"
           + I + "else:\n"
           + I + "    _pos = _T9_POS.get(var_name)\n"
           + I + "    if _pos is None:  # build ONCE per variable, on a cache miss only\n"
           + I + "        _T9_BUILDS[var_name] = _T9_BUILDS.get(var_name, 0) + 1\n"
           + I + "        _pos = {t: i for i, t in enumerate(var_instances)}\n"
           + I + "        _T9_POS[var_name] = _pos\n"
           + I + "    _eff = sorted((t for t in _ref if t in _pos), key=_pos.__getitem__)\n"
           + I + "for var_indices in _eff:\n")
    return "from __future__ import annotations\n" + src.replace(OLD, NEW)
_SRC = {"_compute_inequality_jacobian": _filtered_source(cj._compute_inequality_jacobian, 16, "constraint_expr"),
        "_compute_bound_jacobian": _filtered_source(cj._compute_bound_jacobian, 12, "bound_expr")}
T0 = [time.time()]; EV = []; CNT = {}; CTX = ["other"]
def stamp(n, k): EV.append((round(time.time() - T0[0], 2), n, k))
def timed(mod, attr, tag=None):
    o = getattr(mod, attr)
    def w(*a, **k):
        stamp(attr, "enter"); CTX.append(tag or CTX[-1])
        try: return o(*a, **k)
        finally: CTX.pop(); stamp(attr, "exit")
    setattr(mod, attr, w)
import types as _ty
for a in sorted(dir(cli)):
    f = getattr(cli, a)
    if isinstance(f, _ty.FunctionType) and getattr(f, "__module__", "").startswith("src.") and f.__module__ != "src.cli":
        timed(cli, a, {"compute_objective_gradient": "gradient"}.get(a))
for a, t in (("_compute_equality_jacobian", "equality"),):
    timed(cj, a, t)
_od = cj.differentiate_expr
def _d(*a, **k):
    CNT[CTX[-1]] = CNT.get(CTX[-1], 0) + 1; return _od(*a, **k)
cj.differentiate_expr = _d
_T9_BUILDS = {}
_protos = {}
for _name, _src in _SRC.items():
    ns = dict(vars(cj)); ns["_T9_POS"] = {}; ns["_T9_BUILDS"] = _T9_BUILDS   # captured AFTER the counter
    exec(compile(_src, f"<proto {_name}>", "exec"), ns)
    _protos[_name] = ns[_name]
def _mk(_name, _tag):
    _p = _protos[_name]
    def w(*a, **k):
        stamp(_name, "enter"); CTX.append(_tag)
        try: return _p(*a, **k)
        finally: CTX.pop(); stamp(_name, "exit")
    return w
cj._compute_inequality_jacobian = _mk("_compute_inequality_jacobian", "inequality")
cj._compute_bound_jacobian = _mk("_compute_bound_jacobian", "bound")
class Stop(BaseException): pass  # NOT Exception: src/cli.py catches Exception and sys.exit(1)s, which would mask the cap
signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Stop()))
signal.alarm(CAP)
rc = "?"
try:
    cli.main.main([gms, "-o", out] + (["-vvv"] if os.environ.get("T9_VVV") else ["--quiet"]), standalone_mode=False); rc = "completed"
except Stop:
    rc = "stopped_at_cap"
except BaseException as e:
    rc = f"{type(e).__name__}: {e}"[:200]
json.dump({"rc": rc, "wall": round(time.time() - T0[0], 1), "events": EV, "diff_calls": CNT, "position_map_builds": _T9_BUILDS}, open(pj, "w"), indent=1)
print(rc, round(time.time() - T0[0], 1), CNT, 'map_builds=', _T9_BUILDS)
```

## `cov_one.sh`

```bash
#!/bin/bash
m=$1; pre=$2; R=$REPO_ROOT; cd $R
flag=""; [ "$pre" = 1 ] && flag="--nlp-presolve"
s=$(date +%s)
perl -e 'alarm shift; exec @ARGV' ${T9_CAP:-900} $R/.venv/bin/python -m coverage run --data-file=/tmp/t9/cov/.coverage.$m.$pre --include='*/src/ad/gradient.py' -m src.cli data/gamslib/raw/$m.gms -o /tmp/t9/covout/${m}_$pre.gms --quiet $flag >/dev/null 2>&1
echo "$m $pre rc=$? $(( $(date +%s)-s ))s" >> /tmp/t9/cov_progress.txt
```
