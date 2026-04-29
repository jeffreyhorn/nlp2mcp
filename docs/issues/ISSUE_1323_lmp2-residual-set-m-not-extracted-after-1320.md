# lmp2: Set `m` not extracted into MCP pre-solve, residual after #1320 divisor-guard

**GitHub Issue:** [#1323](https://github.com/jeffreyhorn/nlp2mcp/issues/1323)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** High — `path_syntax_error` (Error 66) prevents PATH from being invoked at all
**Date:** 2026-04-29
**Affected Models:** lmp2
**Predecessors / closely-related:**
- [#1281](https://github.com/jeffreyhorn/nlp2mcp/issues/1281) — Parameter A/b/cc redeclaration (CLOSED, fixed in PR #1314)
- [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243) — Runtime div-by-zero in stat_y (`1/y(p)`)
- [#1315](https://github.com/jeffreyhorn/nlp2mcp/issues/1315) — Multi-solve set assignment not extracted
- [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320) (closed by PR #1321) — bdef divisor guard. **lmp2 was probed as an "adjacent model" but Approach 1 from #1320 did NOT unblock it because lmp2's blocker is structural (set-extraction), not divisor-guard.**

---

## Problem Summary

lmp2's source defines a dynamic subset `m(mm)` whose membership is set
inside a multi-solve `loop(...)` body. The MCP emitter currently emits
references to `m(mm)` in the stationarity equations but **does not
extract the `m(mm) = yes$(...)` set assignment into the MCP pre-solve
section**. Result: GAMS Error 66 on `equation stat_x.. symbol "m" has
no values assigned`.

This is the SAME root-cause class as #1315 (which is filed but
deferred). The post-#1320 reproduction cleanly isolates it: PR #1321
fixed the listing-time div-by-zero issues for gtm but lmp2 was
unaffected by either #1192 or #1320 because its blocker is
**unrelated to listing-time arithmetic** — it's a missing-symbol
compile-time error.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: FAIL (Error 66 — symbol `m` undefined at use)
- **PATH solve**: NOT INVOKED (compile error)
- **Pipeline category**: `path_syntax_error`
- **Predecessors fixed**: #1281 (Parameter dedup, PR #1314)

---

## Reproduction (verified 2026-04-29 with PR #1321 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms \
    -o /tmp/lmp2_mcp.gms --skip-convexity-check
cd /tmp && gams lmp2_mcp.gms lo=2

# Expected output:
# ****  66 equation stat_x.. symbol "m" has no values assigned
# **** 2 ERROR(S)   0 WARNING(S)
# **** USER ERROR(S) ENCOUNTERED
```

Inspect the emitted MCP:

```bash
$ grep -n "m(mm)" /tmp/lmp2_mcp.gms | head -5
# Shows: stationarity equations reference m(mm) but no `m(mm) = yes` line
# is emitted before the equations section.
```

The original lmp2.gms source has the assignment INSIDE the solve loop:

```
loop(s,
   m(mm) = yes$(mp(s, mm));    # ← this assignment is not extracted to MCP
   solve lp using lp minimizing z;
   ...
);
```

---

## Root Cause Detail

`emit_pre_solve_param_assignments` in `src/emit/emit_gams.py` extracts
**parameter** assignments from the source's loop body (Issue #810
mechanism). It does NOT extract **dynamic-subset SET assignments**
(`m(mm) = yes$(...)`) because the existing extraction logic is
keyed on `ParameterDef` and ignores `SetDef` updates.

The MCP emission therefore contains:
1. `Sets ... mm ...` declared (from upstream).
2. `m(mm)` referenced in `stat_x` equation body — but `m` was never
   declared as a SUBSET of mm or assigned membership.
3. GAMS rejects the `m` reference at compile time.

---

## Fix Approach (recommended)

Extend `emit_pre_solve_param_assignments` (or add a sibling
`emit_pre_solve_set_assignments`) to also extract dynamic-subset
SET assignments from the original solve-loop body. The detection:

1. Walk the source's loop tree (already parsed by the dispatcher).
2. For each `LhsConditionalAssign` or plain assignment whose LHS is
   a `SymbolRef` referring to a declared dynamic SET, emit the
   assignment into the pre-solve section before the equations.

This is essentially the same pattern as #1315's recommendation but
applied generically to dynamic-set assignments encountered in the
parsed loop body.

**Estimated effort:** 4–6 hours (locate extraction site, extend
detection, emit set-assignment line, regression test).

### Alternative: emit a default `m(mm) = yes;` if `m` is referenced
but never assigned

Less invasive but semantically incorrect (would over-include rows
that the original NLP excluded via `mp(s, mm)` filter). Not
recommended.

---

## Adjacent Issues for Context

After fixing this set-extraction blocker, lmp2 will likely hit
**#1243** (the `1/y(p)` runtime div-by-zero in `stat_y`). The
ordering: this issue first (compile-blocker), then #1243 (runtime),
then PATH match.

---

## Files Involved

- `src/emit/emit_gams.py` (`emit_pre_solve_param_assignments` and
  surrounding area).
- `src/ir/parser.py` / loop-tree walker.
- `data/gamslib/raw/lmp2.gms` — original source (unchanged).

---

## Acceptance Criterion

1. `gams lmp2_mcp.gms` compiles cleanly (no Error 66 on symbol `m`).
2. lmp2 progresses past `path_syntax_error` to either PATH-solve or
   the next residual blocker (#1243 expected).
3. Stretch: PATH solves to optimal and matches the NLP reference.

---

## Related Issues

- **#1281** (closed) — Parameter redeclaration, fixed in PR #1314
- **#1315** — Multi-solve dynamic-subset set assignment not
  extracted (this issue is a specific instance of #1315's class)
- **#1243** — Next-in-line residual after this is fixed
- **#810** — lmp2 multi-solve loop extraction (parent class issue)
- **#1320** (closed by PR #1321) — Sprint 25 fix that addressed gtm
  but NOT lmp2; this doc clarifies why
