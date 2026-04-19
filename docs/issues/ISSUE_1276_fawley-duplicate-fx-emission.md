# fawley: Emitter Produces Duplicate `.fx` Assignments (nu_pbal.fx, nu_qsb.fx)

**GitHub Issue:** [#1276](https://github.com/jeffreyhorn/nlp2mcp/issues/1276)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Low — Cosmetic (GAMS last-write-wins; no semantic difference), but hints at a real emitter-level dedup gap
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `fawley` (and previously `springchain` — see Related)
**Labels:** `sprint-25`

---

## Problem Summary

The generated `data/gamslib/mcp/fawley_mcp.gms` contains duplicate `.fx` fixation lines for the same multiplier variables. Each of `nu_pbal` and `nu_qsb` is fixed twice:

```gams
nu_pbal.fx(cf,m)$(not (cfq(cf))) = 0;
nu_qsb.fx(cf,l,s)$(not (cfq(cf))) = 0;
nu_pbal.fx(cf,m)$(not (cfq(cf))) = 0;   ← duplicate
nu_qsb.fx(cf,l,s)$(not (cfq(cf))) = 0;  ← duplicate
```

GAMS's last-write-wins semantics means the semantics are unchanged, but the duplicates:

1. Add noise that makes auditing the generated MCP harder.
2. Hint that two different code paths in the KKT/emitter stack each concluded these multipliers should be fixed — they should be computing the same fixation set once, not twice.

---

## Reproduction

```bash
grep -cE "^(nu_pbal|nu_qsb)\.fx" data/gamslib/mcp/fawley_mcp.gms
# → 4  (expected: 2 — one per multiplier)
```

## Suspected Root Cause

The multiplier-fixation emission passes through two code paths that both detect the "this multiplier pairs with a conditionally-empty equation" case and each emit a `.fx` fixation without coordinating. Likely candidates:

- `src/kkt/*.py` classifies multipliers for empty / conditional equations and schedules fixations
- `src/emit/*.py` then re-checks the condition during emit and appends its own fixation

De-duplicating requires either:

- **Upstream dedup**: compute the fixation set exactly once in the KKT classifier, make the emitter a pass-through.
- **Downstream dedup**: collect `(multiplier_name, domain, condition)` tuples during emission and emit each unique tuple once.

Upstream is cleaner if the responsibility is clear; downstream is safer if the two paths have subtly different conditions that should be unioned.

---

## Related Prior Work

- Sprint 23 KU-32 / Sprint 24 KU-24 ("Duplicate `.fx` Emission") flagged the same symptom on `springchain`, with status INCOMPLETE and the hypothesis that it was cosmetic / last-write-wins. The hypothesis stands, but a second model hitting the same pattern confirms the emitter bug is still live.
- No dedicated GitHub issue from that KU — this is the first tracked instance.

---

## Suggested Fix

1. Instrument the fixation emitter to log every `.fx` line it schedules with the call-site, then re-run on fawley to identify the two code paths.
2. Pick the dedup strategy (upstream vs downstream) based on whether the conditions on the two `.fx` lines always match or can legitimately differ.
3. Add a regression test: emit fawley and assert that no `(multiplier, domain, condition)` triple appears twice.

## Out of Scope

- Fawley's underlying infeasibility — tracked separately under KU-18 (Category B PATH convergence).

---

## References

- PR #1273 review comment #3106233156
- Sprint 24 KNOWN_UNKNOWNS KU-24 / Sprint 23 KU-32 (springchain prior observation)
- Sibling Sprint 25 issues: #1275, #1277–#1280

---

## Estimated Effort

1–2 hours (locate the two emission paths + add dedup + regression test).

---

## Files Involved

- `src/emit/*.py` — multiplier `.fx` emission
- `src/kkt/*.py` — multiplier classification for empty / conditional equations
- `data/gamslib/mcp/fawley_mcp.gms` — reference artifact (regenerated after fix)
