# mine MCP infeasible: head-domain-offset equation mis-emits KKT beyond the stat_x cross-term

**GitHub:** #1443
**Status:** DEFERRED → Sprint 29 (re-scoped successor to #1224's Solve gate)
**Filed:** Sprint 28 Day 4 (2026-06-16)

## Summary

Follow-on from #1224. The Sprint 28 Day-4 `stat_x` parameter-valued-offset cross-term inversion landed (correct, tightly gated), but mine still does **not** reach MODEL STATUS 1 — the bug is deeper than the stationarity cross-term.

## Evidence (Day 4)

mine is a **convex LP** (`solve mine maximizing profit using lp`; `Positive Variable x`; `x.up = 1`), so a correct MCP is a well-posed LCP that PATH must solve cleanly cold. After the `stat_x` fix:

- Cold MCP → **MODEL STATUS 5 Locally Infeasible**, `x` blowing up to **~4e10** despite `x.up = 1`.
- **49 INFES** rows spread across `comp_pr`, `comp_lo_x`, `comp_up_x`, `stat_x`, `def` — not localized to stationarity.
- KKT-residual harness still Case b at the NLP warm-start (residual does not vanish even with the corrected `stat_x`).

## Root cause (hypothesis)

The `pr` equation has a **head-domain-offset**: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)` (`has_head_domain_offset = True`). This shape mis-emits the broader KKT, not just `stat_x`. Two concrete sub-issues:

1. **Dual-transfer misalignment (presolve).** `--nlp-presolve` emits `lam_pr.l(k,l,i,j) = abs(pr.m(k,l,i,j))`, but the NLP equation `pr(k,l+1,i,j)` stores its marginal at the `l+1` head-offset position. `comp_pr(k,l,i,j)` (body `x(l,…) - x(l+1,…)`) pairs with `pr.m(k,l+1,i,j)`, so the transfer should read `pr.m` at `l+1`. As emitted, the warm-start duals are off by the head offset (likely in `src/emit/original_symbols.py` / the presolve dual-transfer emit).

2. **Cold infeasibility (deeper).** Even ignoring the warm-start, the cold LP MCP is infeasible (`x → 4e10`) — the emitted complementarity/bound coupling for the head-offset equation is structurally inconsistent. Needs a trace of how `has_head_domain_offset` flows through `comp_pr` emission, the `comp_pr ⊥ lam_pr` pairing, and the bound complementarity (`comp_lo_x`/`comp_up_x` ⊥ `piL_x`/`piU_x`).

## What landed (Day 4, partial — Sprint 28 PR)

The `stat_x` cross-term now matches the hand-derived shape via a tightly-gated symbolic-offset-inversion in `src/kkt/stationarity.py` (`_try_build_param_offset_crossterm`):

```
stat_x(l,i,j).. (... + sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j)) - piL_x(l,i,j) + piU_x(l,i,j))$(d(l,i,j)) =E= 0;
```

Gate fires only on a non-`Const` `IndexOffset` (parameter/symbolic offset = mine only); blast radius = `mine_mcp.gms` `stat_x` line only (launch/camshape/otpop/trnsport byte-identical). Necessary but **not sufficient** for +1 Solve.

## Acceptance

mine cold MCP → MODEL STATUS 1 with objective matching the NLP (`compare_objective_match`). Requires resolving both head-domain-offset sub-issues above.

## Provenance

- #1224 translate fix (Sprint 27 Day 12) — landed (mine translates + compiles).
- #1224 Solve gate `stat_x` inversion (Sprint 28 Day 4) — landed (this PR), correct + gated.
- Remaining head-domain-offset MCP correctness — **this issue (#1443)**, Sprint 29.
