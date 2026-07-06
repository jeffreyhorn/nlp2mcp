# robert: cold MCP converges to a spurious optimum — dropped objective-gradient boundary term in `stat_s`

**GitHub:** (no number — local Sprint-30 P1 sub-track; the genuine-floor half of the head-domain-offset workstream #1443)
**Status:** **Sprint 30 Priority 1 (genuine-floor +1) — PROCEED (standalone objective-gradient fix, ~2–4 h, decoupled from mine).** Established by Sprint 30 Prep Task 3 (`docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md`).
**Filed:** Sprint 30 Prep Task 5 (2026-07-05)

## Summary

robert (Elementary Production and Inventory, an LP — convex) matches its NLP optimum (11025.0) only via the `--nlp-presolve` warm-start (`model_optimal_presolve`); its **cold** MCP solves to MODEL STATUS 1 but a **spurious 6741.67**. Sprint 30 Prep Task 3 re-derived the bug and **refuted the banked ISSUE_1443 Day-12 diagnosis** (which claimed robert's `stat_x` head-offset cross-term should emit `nu_sb(r,tt+1)` instead of `nu_sb(r,tt)`).

**The real bug is a dropped objective-gradient boundary term in `stat_s`** — same class as the Sprint-29 Day-3 #1447 maxmin objvar-scoping fix, **not** the head-domain-offset cross-term. This makes robert a **different bug class from mine** (mine's firm bug is the `comp_pr` `l+1`-head × `li(k)`/`lj(k)`-parameter-offset coupling, `ISSUE_1443` Day-7) → the two do NOT share a fix, and Priority 1 splits into two independent tracks.

## Phase 0: Acceptance Gate

> **Sprint-30 disposition (Prep Task 3, 2026-07-05): PROCEED — standalone objective-gradient fix.** Two cold-solve control experiments on `data/gamslib/mcp/robert_mcp.gms` (self-contained; no warm-start): patching **only** `stat_x` → `nu_sb(r,tt+1)` (the banked "fix") leaves robert at the spurious **6741.67**; patching **only** `stat_s`'s objective gradient (drop-in `-misc("res-value",r)` at `tt=4` + guard `misc("storage-c",r)` to `t(tt)`) makes robert cold-solve to **11025.0 = NLP optimum (MATCH)**. So the `stat_x` cross-term `nu_sb(r,tt)` is already correct under the emit's base-labeling; the objective-gradient `stat_s` fix is necessary **and sufficient**. Decoupled from mine (`ISSUE_1443`).

### Hand-Derived KKT Shape

robert's objective (maximize `profit`) is `pd.. profit =e= sum(t, sum(p, c(p,t)*x(p,t)) - sum(r, misc("storage-c",r)*s(r,t))) + sum(r, misc("res-value",r)*s(r,"4"))`, where `t` (short horizon {1,2,3}) is a subset of `tt` ({1..4}). `s(r,tt)` appears in the objective (storage-c for `tt∈t`; **res-value at `tt="4"`**) and in the base-normalized `sb(r,tt)` (∂ = -1) and `sb(r,tt-1)` (∂ = +1). The correct stationarity of `-profit`:

```
stat_s(r,tt)..  ( misc("storage-c",r)$(t(tt)) - misc("res-value",r)$(ord(tt)=card(tt)) )  * objective gradient
                - nu_sb(r,tt) + nu_sb(r,tt-1)$(ord(tt)>1) - piL_s(r,tt)  =E= 0
```

The `nu_sb` difference part (`- nu_sb(r,tt) + nu_sb(r,tt-1)`) is correct in the current emit. The **objective-gradient part is wrong**: the emit applies `misc("storage-c",r)` for **all** `tt` (no `$(t(tt))` guard) and **drops** the `misc("res-value",r)·s(r,"4")` boundary term — so at `tt=4` it emits `+misc("storage-c",r)` where the KKT needs `-misc("res-value",r)`.

### Expected Emit Pattern

`robert_mcp.gms` `stat_s(r,tt)`'s objective-gradient factor should read `misc("storage-c",r)$(t(tt)) - misc("res-value",r)$(ord(tt)=card(tt))` (not the unguarded `misc("storage-c",r)`). `stat_x(p,tt)`'s head-offset cross-term `sum(r, a(r,p)*nu_sb(r,tt))` is **already correct** (base-labeled) and must **NOT** be changed. (Hypothesis — the actual builder `file:line` to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/robert.gms --json /tmp/phase0_robert.json
```

- **PROCEED (Case b):** harness verdict Case b (Day-0: `max_residual_row = stat_x(high,3)`, rel 7.2 — but this is a **same-index dual-transfer artifact**; the operative bug is in `stat_s`, pinned by the cold-solve control experiment below, not the harness row).
- **Decisive cold-solve control** (self-contained, no dual-transfer artifact): patch `data/gamslib/mcp/robert_mcp.gms` `stat_s` objective gradient → `misc("storage-c",r)$(t(tt)) - misc("res-value",r)$(ord(tt)=card(tt))` and re-solve cold; **expect MODEL STATUS 1 at profit 11025.0** (= NLP ref). Patching `stat_x` → `nu_sb(r,tt+1)` instead leaves 6741.67 (the control that refutes the banked claim).
- **REPLAN:** none applicable — robert is a convex LP (monotone LCP), so no Case-c escape; a correct emit MUST cold-solve. If the objective-gradient fix does not reach 11025 cold, continue the trace (still Case b), do not warm-start.
- Post-fix: cold `compare_objective_match` (11025.0); **add a property-test fixture** for the subset-domain-guarded / fixed-literal-element objective-gradient shape.

### PROCEED/REPLAN Signal

- **🟢 PROCEED — Sprint-30 P1 genuine-floor (Prep Task 3, 2026-07-05).** LOW-risk, standalone, ~2–4 h. Cold-confirmed at 11025 by the control experiment. Independent of mine's head-offset `comp_pr` re-derivation (different bug class). No REPLAN branch (convex LP, no Case-c).
- **Traced Fix-Surface (Day-0) — CONFIRMED (Sprint 30 Day 0, 2026-07-06):** `kkt_residual.py data/gamslib/raw/robert.gms` re-confirms CASE_B, `stat_x(high,3)` rel 7.20, dual transfer CONSISTENT — but that top row is the **same-index transfer artifact** (the harness warm-starts `nu_sb.l=sb.m` at the head label; `TOOLING_READINESS_AUDIT.md` Tool 1). The operative surface is the objective-gradient `stat_s` drop, cold-confirmed by the control experiment (`stat_s`-patch → **11025.0**; `stat_x`-patch → unchanged 6741.67, so `stat_x` is NOT the fix). See `SPRINT_LOG.md` Day 0. The hypothesis stands: the objective-gradient → stationarity emit for `s` — the handling of (a) a **subset-domain objective term** (`misc("storage-c",r)·s(r,t)`, `t` a subset of `tt`) emitted **without** its `$(t(tt))` guard, and (b) a **fixed-literal-index objective term** (`misc("res-value",r)·s(r,"4")`) **dropped** from `stat_s(r,"4")`. Likely `src/ad/gradient.py` (`find_objective_expression` / the per-variable gradient builder) or `src/kkt/stationarity.py` — the **same family as #1447** (objective-term subset-scoping), extended to fixed-literal-element terms. **NOT** the head-offset builder (`stationarity.py:5562`/`:5750`). Trace command: `kkt_residual.py data/gamslib/raw/robert.gms` + the two cold-solve control patches on `robert_mcp.gms` (§Verification). Evidence: `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` §1.
- **Blast-radius note (for Task 9):** the "terminal stock valued at res-value" (`s(r,"last")`) pattern is common in inventory/dynamic models — the fix must be checked corpus-wide.

## Provenance

- Sprint 29 Day 12 (`ISSUE_1443` Day-12 note) — first flagged robert as a head-domain-offset second instance; **that diagnosis is refuted here** (the `stat_x` `nu_sb` index was the wrong surface).
- Sprint 30 Prep Task 3 (`HEAD_OFFSET_ARCHITECTURE_DESIGN.md`) — the re-derivation + the two cold-solve control experiments that pinned the `stat_s` objective-gradient boundary-term bug.
