# robustlp: `defobj(i)` Scalar Equation Over-Indexed, Creates `card(i)` Identical Instances

**GitHub Issue:** [#1279](https://github.com/jeffreyhorn/nlp2mcp/issues/1279)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** High — Silent correctness bug that creates a rank-deficient KKT; likely proximate cause of robustlp's current MODEL STATUS 5
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `robustlp` (primary); any model whose objective-defining equation is scalar in the source but gets domain-widened
**Labels:** `sprint-25`

---

## Problem Summary

In `data/gamslib/mcp/robustlp_mcp.gms` around line 107, the generated `defobj(i)` equation is declared over the full `i` domain, but its body has no `i` dependence — it's semantically scalar:

```gams
defobj(i)..   obj =E= <expression without i> ;
```

This produces `card(i)` identical instances of the same equation, each contributing an identical row to the Jacobian. The corresponding multiplier vector `nu_defobj(i)` is indexed the same way, and `stat_obj` becomes:

```gams
stat_obj..   -1 + sum(i, nu_defobj(i)) =E= 0 ;
```

The multiplier is no longer uniquely determined — PATH sees a rank-deficient Jacobian on those rows. This is very likely the proximate cause of robustlp's current `model_infeasible` (STATUS 5) result, which has been stuck there throughout Sprint 24 with a suspiciously-low residual (~3.6e-04 per KU-18).

---

## Reproduction

```bash
grep -A 2 "^defobj(i)\.\." data/gamslib/mcp/robustlp_mcp.gms
# → defobj(i)..   obj =E= ...  (no i dependence on RHS)

grep "nu_defobj" data/gamslib/mcp/robustlp_mcp.gms | head -5
# → stat_obj references sum(i, nu_defobj(i))
```

## Likely Root Cause

The original `robustlp.gms` source declares the objective-defining equation as **scalar** (no domain). Somewhere in the IR normalization or equation-domain inference step, the domain gets widened to `i`, probably because:

- `i` appears prominently elsewhere in the model as the main set
- The inference rule defaulted the equation's domain to "the dominant set"
- No guard rejected the widening for a body that doesn't reference the set

Scalar equations with scalar objectives must NOT acquire a summation domain — they must emit as plain `defobj..` with a scalar multiplier `nu_defobj` (no parentheses), and `stat_obj` must reference the multiplier directly (not `sum(i, nu_defobj(i))`).

---

## Suggested Fix

1. Audit `src/ir/normalize.py::normalize_model` (and neighbors in `src/ir/`) for equation-domain inference.
2. Find the rule that widens `defobj` from scalar to indexed. Add a guard: if the equation body contains zero references to the candidate domain index, keep the equation scalar.
3. Ensure downstream consumers (KKT assembly, emitter) correctly handle a scalar-equation / scalar-multiplier pairing throughout.
4. Regression-test: robustlp should either (a) recover to optimal/match, or (b) move to a different failure mode that surfaces the next real issue.

## Out of Scope

- robustlp's other Category B characteristics (near-feasible residual, warm-start sensitivity) — tracked under KU-18.
- Any model where `defobj` is **legitimately** indexed (e.g., multiple objective-defining rows): this issue is only for the scalar-body-widened case.

---

## Related

- **KU-18** (Category B PATH convergence, robustlp listed) — Sprint 24 deferred category
- **Sprint 24 Day 13 SPRINT_LOG**: robustlp listed as Category B / deferred; this issue is the single most promising lead for recovering robustlp in Sprint 25

## Regression Guards

After fix:

- `robustlp` pipeline run: infeasibility must disappear or change character (ideally → `model_optimal` or `match`).
- Currently-matching models with scalar `defobj` declarations must continue to produce scalar emission (no new `defobj(...)` domain regressions).

---

## References

- PR #1273 review comment #3106233177
- KNOWN_UNKNOWNS KU-18 (Category B PATH convergence)
- Sibling Sprint 25 issues: #1275–#1278, #1280

## Estimated Effort

3–4 hours (diagnose domain-widening path, targeted fix, verify robustlp recovery).

---

## Files Involved

- `src/ir/normalize.py` — equation-domain inference
- `src/ir/model_ir.py` — equation domain representation
- `src/kkt/*.py` — scalar-multiplier pairing
- `src/emit/*.py` — scalar-equation emission
- `data/gamslib/mcp/robustlp_mcp.gms` — reference artifact (regenerated after fix)
- `data/gamslib/raw/robustlp.gms` — source model
