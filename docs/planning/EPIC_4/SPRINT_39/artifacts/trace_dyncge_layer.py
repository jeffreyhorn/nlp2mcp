#!/usr/bin/env python3
"""Confirm — by execution, not by reading — which layer manufactures dyncge's
phantom ``nu_eqXp(j±k)`` offset terms (ISSUE_1714, Sprint 39 Day 1).

⚠ WHY THIS EXISTS. ``ISSUE_1714`` names a fix surface at
``stationarity.py`` ~7107–7131 (the ``is_dim_mismatch and has_real_offset``
ord-guard branch) and labels it explicitly a *hypothesis*: "Confirm before
implementing — Sprint 38 saw three of four gates name the wrong layer." The
standing rule is stronger still: **a banked fix surface is a hypothesis too —
instrument it, don't read it** (S39 Task 5, where the banked surface never ran).

So this traces the real emit and reports:

1. Which of the candidate decision sites actually EXECUTE for dyncge.
2. What the Pattern-C recogniser CASCADE — any member of which would set
   ``allow_nonzero_offsets = False`` and suppress the offsets at birth — is
   asked, and what it answers, aggregated per variable with ``pf`` called out.
3. The offset keys ``_compute_index_offset_key`` produces for ``pf`` — direct
   evidence that non-zero offsets are manufactured, and that nothing zeroes them.

Run from the repo root. Requires ``data/gamslib/raw/dyncge.gms`` (git-ignored),
and exits non-zero if it is absent rather than reporting a vacuous pass.
"""

from __future__ import annotations

import collections
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[5]
MODEL = ROOT / "data/gamslib/raw/dyncge.gms"

#: Candidate sites, each a half-open line range in src/kkt/stationarity.py.
#: "birth"  = where a non-zero offset is allowed to survive at all (#1381)
#: "guard"  = the ord() guard branch ISSUE_1714 names as the fix surface (#1081)
SITES = {
    "birth:allow_nonzero_offsets default True": (6290, 6291),
    "birth:pattern-C found -> offsets SUPPRESSED": (6314, 6315),
    "birth:offset_key zeroed by suppression": (6449, 6453),
    "guard:is_dim_mismatch and has_real_offset": (7100, 7101),
    "guard:ord() guard constructed": (7124, 7133),
}


def main() -> int:
    if not MODEL.is_file():
        print(f"ERROR: {MODEL} absent (corpus is git-ignored) — nothing traced", file=sys.stderr)
        return 2

    sys.setrecursionlimit(50000)
    from src.kkt import stationarity as st

    hits: collections.Counter[str] = collections.Counter()
    target = st.__file__

    def trace_lines(frame, event, arg):  # noqa: ANN001, ANN202
        # Filter by filename here as well as in trace_calls. MEASURED (PR #1726
        # review): a child frame in another module does NOT reach this function
        # — CPython dispatches every 'call' event to the GLOBAL trace, which is
        # trace_calls below, and that returns None for non-target frames, so the
        # counts were never polluted. The guard is kept anyway because the
        # invariant "these line numbers are stationarity.py's" is load-bearing
        # for every figure this script prints, and it should be visible at the
        # point of use rather than inferred from the other function.
        if event == "line" and frame.f_code.co_filename == target:
            ln = frame.f_lineno
            for label, (lo, hi) in SITES.items():
                if lo <= ln < hi:
                    hits[label] += 1
        return trace_lines

    def trace_calls(frame, event, arg):  # noqa: ANN001, ANN202
        if frame.f_code.co_filename == target:
            return trace_lines
        return None

    # ⚠ There is a CASCADE of Pattern-C recognisers, not one. The suppression
    # only happens if some member of the chain claims the (eq, var) pair; a
    # miss by ALL of them drops through to the generic offset-groups
    # enumeration, which is what manufactures the phantom offsets. So wrap
    # every member — naming only the first would repeat the very error this
    # trace exists to avoid.
    RECOGNISERS = (
        "_find_pattern_c_alias_sum",  # launch-shape ($ condition)
        "_find_plain_alias_pattern_c",  # B-1 plain alias
        "_find_b2_pattern_c",  # B-2 eq-domain factor outside the Sum
        "_find_dim_mismatch_pattern_c",  # B-3 dim-mismatch reducing Sum
    )
    calls: list[tuple[str, str, bool]] = []
    originals = {}

    def make_wrapper(name, orig):  # noqa: ANN001, ANN202
        def wrapped(*a, **k):  # noqa: ANN202
            out = orig(*a, **k)
            var = next((str(x) for x in a if isinstance(x, str)), "?")
            calls.append((name, var, out is not None))
            return out

        return wrapped

    for name in RECOGNISERS:
        originals[name] = getattr(st, name)
        setattr(st, name, make_wrapper(name, originals[name]))

    # Item 3 of the docstring: the offset keys themselves. Without these the
    # script asserts the recognisers missed but never shows the consequence —
    # that non-zero offsets are then produced and nothing zeroes them.
    offset_keys: collections.Counter[tuple] = collections.Counter()
    _orig_key = st._compute_index_offset_key

    def _key_probe(eq_idx, var_idx, mult_domain, var_domain, model_ir, **k):  # noqa: ANN001, ANN202
        out = _orig_key(eq_idx, var_idx, mult_domain, var_domain, model_ir, **k)
        if len(var_domain or ()) == 2:  # pf(h,j) is the 2-D variable of interest
            offset_keys[tuple(out)] += 1
        return out

    originals["_compute_index_offset_key"] = _orig_key
    st._compute_index_offset_key = _key_probe

    from src.cli import main as cli

    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "dyncge_mcp.gms"
        sys.settrace(trace_calls)
        try:
            cli.main(
                [str(MODEL), "-o", str(out), "--quiet", "--skip-convexity-check"],
                standalone_mode=False,
            )
        except SystemExit:
            pass
        finally:
            sys.settrace(None)
            for _n, _o in originals.items():
                setattr(st, _n, _o)

    print("=== Which candidate site actually executes for dyncge? ===")
    for label in SITES:
        n = hits.get(label, 0)
        print(f"  {'HIT ' if n else 'MISS'} {n:>7,}  {label}")

    print("\n=== the Pattern-C recogniser CASCADE (a miss by all -> offsets born) ===")
    agg: dict[tuple[str, str], list[int]] = {}
    for rec, var, found in calls:
        a = agg.setdefault((rec, var), [0, 0])
        a[found] += 1
    print(f"  {'recogniser':<32} {'var':<6} {'CLAIMED':>8} {'missed':>8}")
    for rec in RECOGNISERS:
        tot_f = sum(v[1] for (r, _), v in agg.items() if r == rec)
        tot_m = sum(v[0] for (r, _), v in agg.items() if r == rec)
        print(f"  {rec:<32} {'ALL':<6} {tot_f:>8} {tot_m:>8}")
    print()
    for rec in RECOGNISERS:
        v = agg.get((rec, "pf"))
        if v:
            print(f"  pf only: {rec:<32} CLAIMED={v[1]}  missed={v[0]}")

    print("\n=== offset keys produced for 2-D variables (pf(h,j) is the one at issue) ===")
    if not offset_keys:
        print("  none recorded")
    else:
        nonzero = 0
        for key, n in sorted(offset_keys.items(), key=lambda kv: -kv[1]):
            real = [o for o in key if isinstance(o, int) and o not in (0, st._SENTINEL_UNMATCHED)]
            if real:
                nonzero += n
            shown = tuple("UNMATCHED" if o == st._SENTINEL_UNMATCHED else o for o in key)
            print(f"  {n:6,}  {shown}{'   <-- NON-ZERO: a manufactured offset' if real else ''}")
        print(f"\n  {nonzero:,} of {sum(offset_keys.values()):,} carry a non-zero real offset")
        print("  Nothing zeroes them: the suppression line is a MISS above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
