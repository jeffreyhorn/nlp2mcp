# mine #1443 — Head-Offset Bound-Active Cross-Term: Localization + Re-Derivation Design

**Prep Task:** 3 (Priority 1 foundation) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)
**Status:** design complete — **the banked "cross-term re-derivation" premise is REFUTED by hand-derivation; P1's fix is re-scoped to a head-offset boundary reconciliation** (Unknowns 1.1/1.2 ❌ WRONG, corrected direction below).

> **PR24 discipline:** every fix surface below is a **hypothesis** to be validated by a `/tmp` control **before** any `src/` change. This document sizes and de-risks P1; it does not ship a fix.

---

## 1. Day-0 re-confirm (the control still holds)

`kkt_residual.py data/gamslib/raw/mine.gms` on the current tree (Sprint 32 close `ee51ed9e`):

```
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 0.00e+00 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_x(3,1,1)   rel = 2.37e+00  (raw -3.20e+04)
  stat_x(3,1,1) rel 2.37 · stat_x(1,3,1) rel 1.07 · stat_x(4,1,1) rel 0.82 · stat_x(2,3,3) rel 0.74 · stat_x(3,1,2) rel 0.67
```

CASE_B holds; the **dual transfer is consistent** (complementarity closes at the warm point) yet `stat_x` does not — so the residual is a **stationarity-emit** defect, not a dual-transfer defect. `modelstat` is asserted by the harness; the `x.up=inf` relaxation is **BANNED** (the Sprint-31 measurement-error lesson). This reproduces the Sprint-32 Day-1 `MINE_5TH_COUPLING_REPLAN.md` control (MCP MS-5 @ 22058, 6 wrong-sign bound-active rows).

## 2. NEW localization — the residual is exactly the `c`-boundary

The 6 wrong-sign rows (`MINE_5TH_COUPLING_REPLAN.md` §2) + the max-residual row, classified against `c` and `d` (`card(l)=4`; `c = ord(l)+ord(i)≤card ∧ ord(l)+ord(j)≤card`; `d = …≤card+1`):

| Row | in `d` | in `c` | position |
|---|---|---|---|
| stat_x(3,1,1) [max] | ✓ | ✓ | `ord(l)+ord(i)=4=card` — **on the `c`-boundary** |
| stat_x(1,3,1) | ✓ | ✓ | `ord(l)+ord(i)=4=card` — on the `c`-boundary |
| stat_x(1,3,2) | ✓ | ✓ | on the `c`-boundary |
| stat_x(1,3,3) | ✓ | ✓ | on the `c`-boundary |
| stat_x(3,1,2) | ✓ | ✗ | the **`d\c` ring** (`ord(l)+ord(j)=5=card+1`) |
| stat_x(3,2,1) | ✓ | ✗ | the `d\c` ring |
| stat_x(4,1,1) | ✓ | ✗ | the `d\c` ring |

**Every wrong-sign row sits on the top edge of the pit** — either `ord(l)+ord(i)=card` / `ord(l)+ord(j)=card` (in `c`) or the `d\c` ring (`=card+1`) where `x` is a real variable (in `d`) but no precedence constraint originates (not in `c`). Interior rows have `N=0`. This is a **sharper localization than the banked doc** (which listed the rows but not the boundary pattern) and is the key to the re-scoping in §4.

## 3. The emit site + a from-scratch re-derivation (the cross-term is CORRECT)

**Emitted `stat_x` (`data/gamslib/mcp/mine_mcp.gms:103`):**
```gams
stat_x(l,i,j).. ( (-1)*((conc(l,i,j)*value/100 - cost(l))*1$(d(l,i,j)))
  + sum(k, lam_pr(k,l,i-li(k),j-lj(k))$(c(l,i-li(k),j-lj(k))) - lam_pr(k,l-1,i,j)$(c(l-1,i,j)))
  - piL_x(l,i,j) + piU_x(l,i,j) )$(d(l,i,j)) =E= 0;
```

**Builder:** `src/kkt/stationarity.py::_try_build_param_offset_crossterm` (line 5712) — the Issue-#1224 parameter-offset path (mine is the only corpus model with a non-`Const` `IndexOffset`, `li(k)`/`lj(k)`). It collects the signed body var-refs (`x(l,i+li,j+lj)` +1, `x(l+1,i,j)` −1), inverts each offset (`_negate_index_offset_expr`: `i+li(k)`→`i-li(k)`, `l+1`→`l-1`), keys the multiplier by the inverted indices, and re-indexes the equation condition `c(l,i,j)` via `_reindex_condition_symbols` (→ `c(l,i-li,j-lj)` lead / `c(l-1,i,j)` lag). **Note:** `head_domain_offsets` (the S31 IR foundation) is *not referenced anywhere in `stationarity.py`* — mine's cross-term does **not** flow through it; it flows through `_try_build_param_offset_crossterm`.

**From-scratch re-derivation.** LP: `max profit s.t. g(k,l,i,j) = x(l,i+li(k),j+lj(k)) − x(l+1,i,j) ≥ 0` (declared over `(k,l,i,j)$c(l,i,j)`, head-placed at `(k,l+1,i,j)`), `0 ≤ x ≤ 1`. `lam_pr(k,l,i,j)` pairs with the **body-keyed** `comp_pr(k,l,i,j)$(c(l,i,j) ∧ ord(l)≤card−1)` (`mine_mcp.gms:106`). ∂/∂x(l,i,j):
- `x(l,i,j)` as the `+x(l,·+li,·+lj)` term ⇒ constraint `(k,l,i−li,j−lj)` ⇒ `+lam_pr(k,l,i−li,j−lj)$c(l,i−li,j−lj)`;
- `x(l,i,j)` as the `−x(l+1,·)` term ⇒ constraint `(k,l−1,i,j)` ⇒ `−lam_pr(k,l−1,i,j)$c(l−1,i,j)`.

This is **term-for-term identical to the emit** (labels, signs, conditions), and `lam_pr.fx$(not ord(l)≤card−1)=0` correctly zeroes the out-of-range `l=4` / `l−1=0` instances. **⇒ The cross-term is algebraically correct. Re-deriving it changes nothing.**

## 4. Diagnosis + re-scoping — NOT a cross-term defect

Because (a) the cross-term is verified correct, (b) the dual transfer is consistent (complementarity closes), yet (c) `stat_x` is nonzero *only* on the `c`-boundary, the wrong-sign `N` is **not** a mislabeled/missing cross-term term. It is a **head-offset boundary reconciliation gap**: the original constraint `pr(k,l+1,i,j)$c(l,i,j)` is head-placed at `(k,l+1,i,j)` but the MCP re-keys **both** `comp_pr` and `lam_pr` to the **body** label `(k,l,i,j)`. Complementarity is self-consistent under that re-key (both body-keyed), but the `d\c`-ring variables — `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`, real variables in `d` with **no** precedence constraint of their own (not in `c`) — receive cross-term contributions from boundary `lam_pr` instances (e.g. `stat_x(3,1,2)` and `stat_x(4,1,1)` are coupled through the shared `lam_pr(ne,3,1,1)`) whose bound-active pairing sits at a *different* variable. The result is a residual whose sign demands a **negative** bound multiplier at these rows — infeasible in the MCP.

**This refutes Unknowns 1.1 and 1.2** (the banked premise "re-deriving the one cross-term closes it"). **P1's fix is re-scoped** from *cross-term re-derivation* to a **head-offset multiplier-keying reconciliation**.

### Fix-surface hypotheses (to discriminate with the `/tmp` control, §5)

- **H1 (primary) — head-label multiplier re-keying.** Align the MCP's `comp_pr`/`lam_pr` **and** the `stat_x` cross-term to the **head label `(k,l+1,i,j)`** (where the NLP stores `pr.m`), instead of re-keying to the body label. Concretely: emit `comp_pr` keyed by the head label + invert the `stat_x` cross-term against the head-keyed multiplier. Fix surface (hypothesis): the constraint-keying in the emit pipeline that produces `comp_pr`/`lam_pr` domains + `_try_build_param_offset_crossterm` in `src/kkt/stationarity.py`. This needs IR support for a **head-label-indexed multiplier** (the `head_domain_offsets` foundation is the natural carrier, currently unused by this path).
- **H2 (alternate) — `d\c`-ring bound reconciliation.** Keep body-keying but add the missing stationarity reconciliation for the `d\c`-ring variables (real vars with no originating constraint), so their `stat_x` closes with a ≥0 bound multiplier.
- **H3 (REPLAN exit) — genuinely deeper coupling.** If neither H1 nor H2 drives `N→0` at the `c`-boundary in the `/tmp` control without perturbing interior rows or regressing other head-offset models, the residual is an intrinsic head-offset dual-architecture gap → **REPLAN to a dedicated head-offset dual subsystem** (later sprint).

## 5. The pre-`src/` `/tmp` control (PR24/PR27 gate)

Run **before** any `src/` change; assert `modelstat`; `x.up=inf` BANNED.

1. **Residual decomposition** — hand-edit `mine_mcp_presolve.gms` to `display` each `stat_x` term separately (objective `−cf$d`, `sum_k` term1, `sum_k` term2, `−piL+piU`) at the warm NLP optimum, for all 6 `c`-boundary rows + 3 interior controls. **Gate:** confirm term1/term2 match the hand-derivation (they should — the cross-term is correct) and isolate which component carries the wrong sign at the ring vs the `c`-edge.
2. **H1 patch prototype** — hand-edit the two transfer/emit lines to head-label-keyed `lam_pr` (`comp_pr` at `(k,l+1,i,j)`; `stat_x` cross-term inverted against it). **Gate:** the warm residual `N → 0` at **all 6** bound-active rows AND unchanged (`0`) at every interior row; then presolve to **MS-1 at profit 17500** (`modelstat=1` asserted). No wrong-sign `N`.
3. **No-regression probe** — confirm the H1 shape does not perturb the interior emit for the other head-offset/param-offset corpus members (srpchase and any `_try_build_param_offset_crossterm` user) via a spot re-emit + `--resolve-changed --since-commit ee51ed9e` GO before the src change lands.

**PROCEED** (H1) iff probe 2 closes `N→0` at MS-1 and probe 3 is clean; else **PROCEED** (H2) iff its variant closes; else **REPLAN** (H3).

## 6. Sizing + REPLAN exit

**18–24 h** (upper half, **~22–24 h**, given the re-scope from a sign/guard tweak to a multiplier-keying change):
- `/tmp` residual decomposition + H1/H2 prototype + gate (~5–7 h) — the Phase-0 control.
- Head-label multiplier-keying emit + IR plumbing (`comp_pr`/`lam_pr` head-label domain via `head_domain_offsets`; `_try_build_param_offset_crossterm` inversion against it) (~10–14 h).
- Determinism ×3 + golden-staleness + `--resolve-changed` + regression tests (shape12 fixture) (~3–4 h).

**REPLAN exit (H3):** if the `/tmp` H1/H2 prototype cannot drive `N→0` at the `c`-boundary without perturbing interior rows or regressing srpchase, mine stays `model_infeasible` and P1 hands off a dedicated head-offset dual-architecture subsystem to a later sprint — **no `src/` shipped** (the 7th consecutive control-first disposition). The de-risked hand-off is this document + the residual decomposition.

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **1.1** | ❌ **WRONG** | The wrong-sign `N` is **not** produced by a cross-term term error — the cross-term is verified algebraically correct (re-derivation + source trace). The defect is a head-offset boundary reconciliation. |
| **1.2** | ❌ **WRONG** | No sign/guard correction on the cross-term exists (it is already correct); the fix is head-label multiplier re-keying (H1) or `d\c`-ring reconciliation (H2). |
| **1.3** | ✅ VERIFIED | `head_domain_offsets` exists but is **unused** by mine's path (`_try_build_param_offset_crossterm`, not the head-offset IR). The H1 fix needs a head-label-indexed multiplier — new IR/emit plumbing (the natural carrier is `head_domain_offsets`). |
| **1.4** | ✅ VERIFIED | The harness asserts the verdict; the `/tmp` control asserts `modelstat` and BANS `x.up=inf`. |
| **1.5** | ✅ VERIFIED | 18–24 h realistic but at the **upper half (~22–24 h)** given the re-scope; the deeper-coupling REPLAN exit (H3) is pinned. |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)
