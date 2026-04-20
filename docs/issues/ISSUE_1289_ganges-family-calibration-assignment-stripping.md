# Emitter: ganges-family calibration-assignment stripping (ganges, gangesx unblocked)

**GitHub Issue:** [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289)
**Status:** OPEN — Sprint 25 Priority 2
**Severity:** High — Blocks 2 of 5 Sprint 25 Priority 2 recovered-translate models (`ganges`, `gangesx`) from reaching any `model_optimal` outcome
**Date:** 2026-04-20
**Affected Models:** `ganges`, `gangesx`
**Discovered:** Sprint 25 Prep Task 5 (recovered-translate leverage analysis)
**Labels:** `sprint-25`

---

## Problem Summary

The emitter strips parameter-calibration assignments when translating NLPs that use the "declare-params + initial-solve + calibrate-from-`.l`-values" pattern. The resulting MCP declares the parameters but never assigns values, producing GAMS `Error 66: Use of a symbol that has not been defined or assigned` at the MCP compile step.

## Reproduction

```bash
gams data/gamslib/mcp/ganges_mcp.gms action=c lo=2
# -> 16 × Error 66 — symbols deltax, aid, aex, adst, as, deltas, av, deltav,
#                   aq, deltaq, az, deltaz, an, deltan, pnm00, cg undefined
# -> 2 × final error, 256 solve-stmt errors, compile rejected
```

## Source Pattern (ganges.gms, lines 332–602)

1. Parameters declared with domain-only declarations (lines 332–355)
2. Initial-solve block (runs NLP with literal starting values)
3. Calibration from post-solve `.l` values (lines 598–602):

```gams
deltas(i)$ls.l(i) = (k(i)/ls.l(i))**(1/sigmas(i))*pk.l(i)/sum(r$ri(r,i), pls.l(r));
deltas(i)$ls.l(i) = deltas(i)/(1 + deltas(i));
deltas(i)$(not ls.l(i)) = 1;
as(i) = s.l(i)*(deltas(i)*k(i)**(-rhos(i)) + ...)**(1/rhos(i));
```

When nlp2mcp translates, the emitter includes the Parameter declarations (step 1) but drops the calibration block (step 3). MCP compile then fails because the parameters are referenced by stationarity equations (`stat_ax`, `stat_ls`, etc.) with no values assigned.

## Likely Root Cause

The IR-to-emitter pipeline strips statements that reference variable levels (`.l`, `.m`, `.lo`, `.up`) because those are post-solve quantities. For the calibration-from-solve pattern, this is incorrect: those assignments MUST be emitted in the MCP, wrapped with the `--nlp-presolve` `$include` mechanism so the initial-solve populates the `.l` values first.

## Candidate Fixes

1. **Preserve calibration assignments:** detect "Parameter declared without inline values AND later assigned from `.l` values" pattern; emit both, wrapped to run after the presolve `$include`.
2. **Require `--nlp-presolve`:** flag calibration-pattern models; require the flag to translate them.
3. **Audit IR normalization** for the statement-stripping pass.

## References

- Sprint 25 Prep Task 5: `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Sibling new issues: #1290, #1291, #1292

## Estimated Effort

4–6h

## Files Involved

- `src/ir/normalize.py` — statement-stripping pass
- `src/emit/emit_gams.py` — calibration-block emission
- `data/gamslib/raw/ganges.gms`, `data/gamslib/raw/gangesx.gms` — reference sources
- `tests/unit/emit/` — new emitter test
