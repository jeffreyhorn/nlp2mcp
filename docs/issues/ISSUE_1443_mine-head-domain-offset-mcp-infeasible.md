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

## Day-4 root-cause probe (2026-06-16, ~2h time-box — NO-GO for an ≤8h fix)

Time-boxed probe to decide go/no-go on fixing this in the remaining Day-4 budget. Method: warm-start mine's MCP at its NLP solution and drive the `stat_x` residual to ~0 by varying the dual transfer; measure `max|stat_x residual|` (`Val - Lower`) at `iterlim=0`.

**Findings:**
- The embedded NLP (LP) solves **MODEL STATUS 1 Optimal** and **does produce duals** — `pr.m` has 14 nonzero entries, `x.m` (reduced costs) has 11. So the duals exist; they are not being captured/aligned into the MCP multipliers.
- The duals live at the **`l+1`-shifted equation instances** (e.g. `pr.m(ne,2,1,3) = -1500` is the dual for controlling `(ne,1,1,3)`), because `pr` is declared `pr(k,l+1,i,j)`. The production transfer `lam_pr.l(k,l,i,j) = abs(pr.m(k,l,i,j))` reads the wrong instance.
- **No `lam_pr` sign×alignment variant zeroed the residual.** Tried `abs(pr.m(k,l,i,j))` (baseline, 1.8e4), `abs(pr.m(k,l+1,i,j))` (3.2e4), `+/-pr.m(k,l+1,i,j)` (1.6e4 / 3.2e4), `+/-pr.m(k,l,i,j)` (1.6e4 / 1.8e4). Best is **1.6e4** — nowhere near 0.
- At the worst cell `stat_x(3,1,1)` the residual is the **bare profit gradient (16000)** with `lam_pr`, `piL_x`, `piU_x` all ≈ 0 there — the balancing duals are not landing at the indices `stat_x` reads.

**Verdict:** the root cause is a genuine **head-domain-offset index-correspondence** problem between the NLP's `l+1`-shifted dual instances and the MCP's normalized `comp_pr`/`lam_pr`/`stat_x` indexing. The duals are present but mis-aligned, and a single sign/alignment tweak does **not** resolve it — the fix needs a careful, coordinated re-derivation of the head-offset index map across **three** emit sites (`comp_pr` emission, the `--nlp-presolve` dual transfer, and the `stat_x` cross-term), plus the cold-start LCP consistency. This was **not** crackable in the probe time-box and is **not** a confident ≤8h fix. **Confirmed Sprint 29.** (Also revisit whether `lam_pr.l = abs(pr.m)` has a sign issue — the `abs()` may be the Day-2 `nu`-class sign-flip.)

### Pushed-further check (post-time-box, 2026-06-16) — confirms SYSTEMIC, no clean fix

Continued past the time-box (maintainer-approved) to attempt a fix. With the principled `l+1` alignment (`lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))`), the `stat_x` residual is **systemic, not boundary**: **22 of 30** `stat_x` cells exceed 1e-3 (residuals 1000–14500, all "round" multiples of ~500 — the fingerprint of sign-flipped / mis-aligned dual contributions, not numerical noise). The `stat_x` cross-term *formula* was re-derived and confirmed correct against `comp_pr`'s body; so the systemic imbalance is in the **dual values reaching the wrong indices/sign**, coupled across the transfer + the bound multipliers (`piU_x` likely never set if the MCP leaves `x.up = +inf` and routes the upper bound through `comp_up_x`). Because no single change zeroes the residual and the correct fix is a multi-site re-derivation, **there is no safe code change to land** — pushing further only sharpened the Sprint-29 scope (it did not produce a fix). **No `src/` change committed.**

## Acceptance

mine cold MCP → MODEL STATUS 1 with objective matching the NLP (`compare_objective_match`). Requires resolving both head-domain-offset sub-issues above.

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 4, 2026-06-25):** harness verdict **Case b**, `max_residual_row = stat_x('4','1','1')`, rel = **1.333**, dual-transfer consistent. **PROCEED.** Critically, **mine is a convex LP** (Unknown 1.3): its MCP is a **monotone** LCP — no spurious local solutions (a degenerate, non-unique optimum is fine; all LP optima share the same objective), so a correct emit MUST cold-solve — there is **no warm-start escape** and **no Case-c exit** (cold infeasibility here *is* the emit bug, not non-convexity). This makes mine a **genuine +1 Solve** target (`model_infeasible → model_optimal`), unlike the non-convex cold-convex cohort.

### Hand-Derived KKT Shape

The head-domain-offset constraint `pr(k,l+1,i,j)$c(l,i,j)..  x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)` (`li`/`lj` parameter offsets) couples three normalized emit sites. With `comp_pr(k,l,i,j)` body `x(l,i+li(k),j+lj(k)) - x(l+1,i,j)` paired with `lam_pr ≥ 0`, the `x`-stationarity must invert the parameter offset on the head term and the `l+1` shift on the tail:

```
stat_x(l,i,j)$d(l,i,j)..  ∂profit/∂x(l,i,j)
   + sum(k, lam_pr(k, l, i-li(k), j-lj(k)) - lam_pr(k, l-1, i, j))
   - piL_x(l,i,j) + piU_x(l,i,j)   =E= 0
```

The `stat_x` cross-term formula landed (Sprint 28 Day 4) and is correct against `comp_pr`'s body. The residual persists because the **dual values reach the wrong indices/sign**: the NLP stores `pr.m` at the `l+1`-shifted instances (`pr` declared `pr(k,l+1,i,j)`), so the presolve transfer `lam_pr.l(k,l,i,j)=abs(pr.m(k,l,i,j))` reads the wrong instance, and the upper bound is likely routed through `comp_up_x` with `piU_x` never set.

### Expected Emit Pattern

A consistent head-offset index map across **three** sites: (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer `lam_pr.l = … pr.m(k,l+1,…)` (head-offset-aligned, sign-checked vs the `nu`-class flip), (3) the `stat_x` cross-term (landed). All three must agree on the `l+1`/`±li`/`±lj` correspondence, and the cold LCP must be feasible (`x ≤ x.up=1`, no `x→4e10` blowup). (Hypothesis — to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms --json /tmp/phase0_mine.json
# Cold-solve feasibility check (must reach MODEL STATUS 1, x bounded by x.up=1):
.venv/bin/python -m src.cli data/gamslib/raw/mine.gms -o /tmp/mine_mcp.gms --quiet && cd /tmp && gams mine_mcp.gms lo=0
```

- **PROCEED (Case b):** `max_residual_row = stat_x(...)`, rel ≈ 1.33 (✅ Day-0); the residual localizes to the head-offset dual-transfer/bound coupling. Because mine is **convex**, Case b is the expected verdict and there is no Case-c alternative.
- **REPLAN (Case c):** would require mine to be non-convex with multiple optima — **ruled out** (convex LP). If, after the 3-site fix, the cold LCP is still infeasible, the failure is a residual **emit/index-map** bug (still Case b), not non-convexity → continue the trace, do **not** REPLAN to warm-start.
- Acceptance: cold MCP → MODEL STATUS 1 with `compare_objective_match` to the NLP.

### PROCEED/REPLAN Signal

- **PROCEED** — Day-0 Case b on `stat_x`, rel ≈ 1.33 (✅), convex LP ⇒ no Case-c escape ⇒ genuine +1 Solve.
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the head-offset dual transfer in `src/emit/original_symbols.py` (the `--nlp-presolve` `lam_pr.l = abs(pr.m(...))` instance/sign), the `comp_pr` emission, and the bound complementarity (`comp_up_x ⊥ piU_x`). The Day-4 probe (this doc) localized the symptom: 22/30 `stat_x` cells systemic, "round" residuals = mis-aligned dual contributions. Trace command: `--keep-files` the residual scratch + dump `pr.m`/`lam_pr.l`/`piU_x.l` at the NLP point; cite the `file:line` where the `l+1`/`±li`/`±lj` index correspondence is built. **Note (Task 5):** the PROCEED/REPLAN *decision* (is the 3-site re-derivation an ≤8h fix?) is finalized by Task 5 — the Day-4 time-box flagged it as multi-site and not a confident ≤8h fix.

## Provenance

- #1224 translate fix (Sprint 27 Day 12) — landed (mine translates + compiles).
- #1224 Solve gate `stat_x` inversion (Sprint 28 Day 4) — landed (this PR), correct + gated.
- Remaining head-domain-offset MCP correctness — **this issue (#1443)**, Sprint 29.
