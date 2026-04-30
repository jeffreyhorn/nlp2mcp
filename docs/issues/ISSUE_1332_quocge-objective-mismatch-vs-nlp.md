# quocge: PATH solves to Optimal but objective value mismatches NLP reference

**GitHub Issue:** [#1332](https://github.com/jeffreyhorn/nlp2mcp/issues/1332)
**Status:** OPEN
**Severity:** Low-Medium — model solves successfully but with a different KKT point than the NLP. May or may not be acceptable depending on whether quocge is non-convex (multiple local optima legitimately exist).
**Date:** 2026-04-30
**Affected Models:** quocge

---

## Problem Summary

After PR #1329 (#1245), quocge compiles cleanly and PATH solves to
`MODEL STATUS 1 Optimal`, but the resulting `UU.l` value differs from
the original NLP solve:

| | Value |
|---|---|
| NLP reference (`gams quocge.gms`) | **25.5085** |
| MCP (post-#1245) | **25.6829** |
| Relative difference | **+0.68%** |

The KKT system is structurally correct (PATH found a feasible point),
but the converged point is not the same as the NLP's local optimum.

---

## Current Status

- **Translation:** Success
- **GAMS compilation:** Success
- **PATH solve:** `MODEL STATUS 1 Optimal`, `nlp2mcp_obj_val = 25.683`
- **Original NLP:** `MODEL STATUS 2 Locally Optimal`, `OBJECTIVE VALUE 25.5085`
- **Pipeline category:** `model_optimal` but `solution_comparison: mismatch`

---

## Reproduction (verified 2026-04-30 with PR #1329 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/quocge.gms -o /tmp/quocge_mcp.gms --quiet
cd /tmp && gams quocge_mcp.gms lo=0
grep -E "MODEL STATUS|nlp2mcp_obj_val" /tmp/quocge_mcp.lst
# **** MODEL STATUS      1 Optimal
# ----    643 PARAMETER nlp2mcp_obj_val      =       25.683

# Compare with NLP:
gams /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/quocge.gms lo=0
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE               25.5085
```

---

## Hypothesis

Several plausible root causes, ordered by likelihood:

1. **Non-convexity / multiple local optima.** quocge uses CES utility
   (`UU = prod(i, X(i)**alpha(i))` style) with `sigma(i) = 2`,
   `psi(i) = 2`. Cobb-Douglas/CES with shares summing to 1 is convex
   in log-space but may have multiple stationary points in the
   primal. PATH finds a different KKT point than the NLP solver. If
   verified, this is documented behavior, not a bug. Document and
   close as "wontfix — non-convex, different but valid local optimum".

2. **AD or simplification bug specific to quocge's expression shape.**
   quocge has unique structure relative to other CGE-family models —
   it's a "quotient CGE" (Devarajan, Lewis, Robinson) with explicit
   quotient terms. If the AD pipeline mishandles a specific term
   (alias-AD per #1138 family, or a specific function derivative),
   the stationarity system would have a wrong row, and PATH converges
   to a different (and incorrect) point.

3. **Bound multiplier interaction.** The CGE family uses `.lo = .01`
   bounds on prices and quantities. PATH may bind some of these
   bounds at the optimum that the NLP solver does not, producing
   non-trivial bound multipliers and a different solution.

---

## Investigation Steps

1. **Compare per-variable solutions:** dump `<var>.l` from the NLP
   `.lst` and from the MCP `.lst`. Identify which variables differ
   most. Cluster: are they all in the production block, all in the
   trade block, or scattered?

2. **Check for active bound multipliers in MCP:** `grep "piL_.*\.l\s*=" /tmp/quocge_mcp.lst | grep -v "= 0\."` — find non-zero bound multipliers. If many bounds are active in MCP but not NLP, that's a starting-point issue (Approach 3 from #1245's residual camcge plan).

3. **Run with `--nlp-presolve`:** if the warm-start path works on
   quocge (unlike camcge), the warm-started MCP should match the NLP.
   If it does, this is purely a starting-point issue and the fix is
   warm-starting from the NLP solution.

4. **Compare KKT residuals:** evaluate the KKT system at the NLP's
   solution and at PATH's solution. If both satisfy the KKT to high
   precision, both are valid local optima — the model is non-convex.

5. **Check for #1138 alias-AD pattern:** quocge may share aliases
   `(u,v)`, `(i,j)`, `(h,k)` with irscge / lrgcge / moncge / stdcge.
   If so, the same gradient-mismatch root cause may apply (though
   note: irscge / lrgcge / moncge / stdcge currently match post-#1245
   in this same regression sweep, so #1138 may already be resolved or
   inactive on those models).

---

## Fix Approach

Depends on the investigation above. Likely paths:

### Path A — Document as non-convex local-optimum (close as wontfix)

If §Investigation step 4 shows both solutions satisfy KKT, this is
correct behavior on a non-convex model. Document the comparison
mechanism's behavior on non-convex CGE and close. Cost: 1–2 hours.

### Path B — Warm-start fix

If `--nlp-presolve` resolves the mismatch, file follow-up to ensure
the presolve path is robust on the CGE family. Cost: 4–6 hours
(possibly bundled with the camcge `--nlp-presolve` fix).

### Path C — AD bug fix

If §Investigation step 5 reveals an alias-AD or term-specific bug
that's quocge-unique, file follow-up with concrete reproduction.
Cost: depends on AD bug nature, likely 6–12 hours.

---

## Estimated Effort

3–6 hours for investigation. Total cost depends on the path:
- Path A: +1h to document
- Path B: +4–6h to fix presolve
- Path C: +6–12h depending on AD bug

---

## Acceptance Criterion

1. ✅ Investigation completed: which path applies (A, B, or C)?
2. ✅ If Path A: documentation explains why mismatch is acceptable;
   pipeline comparison logic relaxed for non-convex CGE.
3. ✅ If Path B: warm-started MCP matches NLP within 1e-3.
4. ✅ If Path C: AD fix lands; quocge matches NLP within 1e-3.

---

## Files Involved

- `data/gamslib/raw/quocge.gms` — original source
- `/tmp/quocge_mcp.gms` and `/tmp/quocge_mcp.lst` — MCP and listing
- `src/ad/*.py` — if AD bug suspected (Path C)

---

## Related Issues

- **#1245** (CLOSED, PR #1329) — wrapped traded-only multiplier terms;
  unblocked quocge to reach MODEL STATUS 1.
- **#1138** — CGE-family alias-AD mismatch (irscge / lrgcge / moncge
  / stdcge — possibly applies here too).
- **#1192** — gtm warm-start pattern (related: gtm needs
  `--nlp-presolve` for objective match).
