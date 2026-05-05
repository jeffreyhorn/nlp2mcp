# fawley: PATH $171 Domain Violations in Stationarity (Post-#1276 Fix Bucket Transfer)

**GitHub Issue:** [#1356](https://github.com/jeffreyhorn/nlp2mcp/issues/1356)
**Status:** OPEN — Sprint 26 carryforward (filed Sprint 25 Day 13)
**Severity:** Medium — model translates cleanly post-Sprint-25 fixes but PATH compilation fails with 3 `$171` errors
**Date:** 2026-05-05
**Last Updated:** 2026-05-05
**Affected Models:** fawley (confirmed); root cause not yet localized — may share family with #1357 (otpop)

---

## Problem Summary

After Sprint 25 closed #1276 (duplicate `.fx` emission), #1133 (empty mbal SetMembershipTest), and #1130 (table column alignment), the Day 11 retest shows fawley moved from `model_infeasible` to **`path_syntax_error`** — the emitted MCP now fails GAMS compilation with **3 `$171`** ("Domain violation for set") errors plus a downstream `$141`.

One of the four bucket additions during Sprint 25 (see SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation").

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/fawley.gms \
  -o /tmp/fawley_mcp.gms --skip-convexity-check --quiet
gams /tmp/fawley_mcp.gms lo=2

# *** Error 171 in /tmp/fawley_mcp.gms (line 273 ×2, line 315)
# *** Error 257 (cascade)
# *** Error 141 in /tmp/fawley_mcp.gms (line 381)
# *** Status: Compilation error(s)
```

---

## Diagnostic

GAMS error `$171` means a stationarity equation references a variable / parameter at an index outside the declared domain. Possible mechanisms:

1. `nu_<eq>(i)` with `i` taken from a superset (subset/superset domain confusion — same shape as the otpop issue #1175 that closed earlier).
2. An IndexOffset (`i+N`) that lands outside the multiplier's declared subset domain.
3. Aliased index mis-binding in the stationarity assembly path.

Without a deeper inspection of lines 273 / 315 of the emitted `fawley_mcp.gms` and a hand-trace back to which source equation produced them, the root cause is not yet localized — Sprint 26 should start with the `.lst`-line cross-reference.

---

## Where to Investigate (Sprint 26 Day 0 / 1)

1. Open `/tmp/fawley_mcp.gms` (regenerate per "Reproduction" above) and inspect lines 273 and 315.
2. Match each violating reference back to its source equation in `data/gamslib/raw/fawley.gms`.
3. Determine whether the violation is:
   - **Pattern C variant** (likely shared with #1354 / #1355 — phantom IndexOffset onto a multiplier's subset domain).
   - **Subset-superset confusion** (similar to closed #1175 otpop, which was Sprint 23/24 work — may indicate a regression).
   - **Domain-widening misalignment** (the multiplier's `declaration_domain` machinery from #1327 may be misaligned for fawley).

---

## Tests to Add

- **Integration test** in `tests/integration/emit/`: assert fawley's emitted MCP compiles cleanly under GAMS `lo=2` (or, more narrowly, asserts no `$171` substring in the `.lst` file). Currently no such regression test exists.
- Once root cause is identified, add a unit test in `tests/unit/kkt/` against the specific stationarity assembly path.

---

## Files Involved (preliminary — pending Sprint 26 root-cause)

- `src/kkt/stationarity.py` — likely
- `src/kkt/complementarity.py` — possible (if `multiplier_domain_widenings` arity mismatch)
- `data/gamslib/raw/fawley.gms` — source
- `data/gamslib/mcp/fawley_mcp.gms` — current buggy emit

---

## Estimated Effort

**4–8h** for diagnosis (line-by-line cross-reference + minimal repro extraction), then variable depending on root cause:
- If shared with **#1354 / #1355** (Pattern C variant): subsumed by that fix.
- If new: standalone ~6–10h.

---

## Related

- **#1276** (duplicate fx emission — CLOSED Sprint 25)
- **#1130** (table column alignment — CLOSED earlier)
- **#1133** (empty mbal SetMembershipTest — CLOSED earlier)
- **#1175** (otpop subset-superset domain violation — CLOSED; same `$171` shape, predecessor)
- **#1354 / #1355** (camcge / cesam2 phantom IndexOffset — possible shared Pattern C variant)
- **#1357** (otpop `$171` — also in the four-bucket-additions cohort; possibly same root cause)
