# Head-Domain-Offset Emit-Architecture Design + robert Minimal Reproduction

**Task:** Sprint 30 Prep Task 3 (Priority 1 foundation — the critical-path anchor)
**Date:** 2026-07-05
**Owner:** Development team (AD/KKT specialist)
**Scope:** design/analysis only — no `src/` change (all probes were `/tmp` copies, reverted; the committed goldens are untouched).

---

## 0. Executive summary — a PR24 correction that re-scopes Priority 1

This task set out to (a) hand-derive robert as the *pure-constant-offset minimal reproduction* of mine's head-domain-offset bug, (b) design a single 3-site head-offset index-map that converts **both** mine (Solve) and robert (genuine-floor), and (c) validate that robert generalizes to mine. **Empirical re-derivation refuted the banked premise.** The headline findings:

1. **robert's real bug is NOT the head-offset cross-term.** The Sprint-29 Day-12 banked diagnosis (`ISSUE_1443`: "robert's `stat_x` emits `sum(r, a(r,p)*nu_sb(r,tt))` but should be `nu_sb(r,tt+1)`") is **wrong**. robert's `stat_x` cross-term `nu_sb(r,tt)` is **already correct** under the emit's base-labeling of `sb(r,tt)`. robert's actual bug is a **dropped objective-gradient boundary term** in `stat_s`: the horizon-end inventory valuation `res-value(r)·s(r,"4")` is omitted and the `storage-c(r)` term is applied outside its `t(tt)` subset domain.
2. **Decisive control experiment (cold MCP, no warm-start):** patching **only** `stat_s`'s objective gradient (storage-c → `−res-value` at `tt=4`) makes robert's cold MCP solve to **profit = 11025.0 = the NLP optimum (MATCH)**; patching **only** `stat_x` to `nu_sb(r,tt+1)` (the banked "fix") leaves it at the spurious **6741.67**. → the operative bug is entirely in `stat_s`; the `stat_x` index is a red herring.
3. **robert is therefore NOT a minimal reproduction of mine.** robert's bug is an **objective-gradient scoping** bug (the same class as the Sprint-29 Day-3 #1447 maxmin objvar fix). mine's firm bug (`ISSUE_1443` Day-7) is a **constraint-Jacobian head-offset × parameter-offset coupling in `comp_pr`** — a different class. **Unknown 1.1 = ❌ does NOT generalize.**
4. **Favourable outcome: Priority 1 splits into two independent tracks.** robert (genuine-floor +1) is a **low-risk, standalone objective-gradient fix** (~2–4 h, decoupled from the head-offset architecture); mine (+1 Solve) is the **high-risk multi-site `comp_pr` re-derivation** (~10–16 h, REPLAN-prone). Removing the false coupling *de-risks* the robert genuine-floor gain and correctly isolates mine as the hard track.

---

## 1. robert — the actual bug, empirically pinned

### 1.1 The model (the head-domain-offset stock balance)

`data/gamslib/raw/robert.gms` (Elementary Production and Inventory, LP — convex):

```gams
sb(r,tt+1)..  s(r,tt+1) =e= s(r,tt) - sum(p, a(r,p)*x(p,tt));                       * head-domain-offset
pd.. profit =e= sum(t, sum(p, c(p,t)*x(p,t)) - sum(r, misc("storage-c",r)*s(r,t)))  * storage cost, t = short horizon {1,2,3}
             +  sum(r, misc("res-value",r)*s(r,"4"));                                * TERMINAL inventory valuation at tt = "4"
```

`sb(r,tt+1)` is genuinely a head-domain-offset equation (the head index carries `+1`). But — critically — the objective `pd` also carries a **fixed-literal-index boundary term** `res-value(r)·s(r,"4")` that values leftover stock at the end of the horizon.

### 1.2 The emitted cold golden (`data/gamslib/mcp/robert_mcp.gms`)

```gams
stat_x(p,tt).. ( -c(p,tt)$(t(tt)) + sum(r, a(r,p)*nu_sb(r,tt)) + lam_cc(tt)$(t(tt)) - piL_x(p,tt) )$(t(tt)) =E= 0;
stat_s(r,tt).. ( misc("storage-c",r) - nu_sb(r,tt) + nu_sb(r,tt-1)$(ord(tt)>1) - piL_s(r,tt) )$(...) =E= 0;
sb(r,tt)$(ord(tt) <= card(tt)-1).. s(r,tt+1) =E= s(r,tt) - sum(p, a(r,p)*x(p,tt));   * normalized to BASE label
```

The emitter **normalizes** the head-offset equation to the base label `sb(r,tt)$(ord(tt)<=card-1)` (tt = 1,2,3) with multiplier `nu_sb(r,tt)`. Under this convention the body of `sb(r,tt)` references `x(p,tt)` at the **base** index, so `∂sb(r,tt)/∂x(p,tt) = a(r,p)` and the `stat_x` cross-term `sum(r, a(r,p)*nu_sb(r,tt))` is **internally consistent and correct**. (The banked diagnosis compared against a *head-labeled* convention the emitter does not use.)

### 1.3 Hand-derived KKT for `s(r,tt)` vs the emit — the boundary-term drop

`s(r,tt)` appears in: the objective (storage-c for `tt∈t`; **res-value at `tt="4"`**), and in `sb(r,tt)` (∂ = −1) and `sb(r,tt-1)` (∂ = +1). The correct stationarity of `−profit`:

| tt | correct objective-gradient term | emitted term | match? |
|----|-------------------------------|--------------|--------|
| 1,2,3 (`t(tt)`) | `+ storage-c(r)` | `+ storage-c(r)` | ✅ |
| 4 (horizon end) | `− res-value(r)` | `+ storage-c(r)` | ❌ **wrong** |

So the emit (a) applies `storage-c(r)` **without its `t(tt)` guard** (leaking it to `tt=4`), and (b) **drops the `res-value(r)·s(r,"4")` boundary term entirely**. The `nu_sb` difference part (`− nu_sb(r,tt) + nu_sb(r,tt-1)`) is correct.

Evaluated at the NLP optimum, the corrected `stat_s(r,4)` residual → **0** (clean, since `s(r,4)` is interior so its bound multiplier is 0); the emitted term leaves a residual of `storage-c(r)+res-value(r)` = +15.5 (scrap) / +27 (new).

### 1.4 The decisive cold-solve experiments

The cold MCP is self-contained (no NLP warm-start), so a cold solve to the wrong objective is an unambiguous emit bug. NLP reference = **11025.0**.

| Experiment | Cold MCP result |
|---|---|
| **Baseline golden** (as committed) | MS 1, profit **6741.67** — spurious KKT point (MISMATCH) |
| Patch **`stat_x` only** → `nu_sb(r,tt+1)` (the banked "fix") | MS 1, profit **6741.67** — **still wrong** |
| Patch **`stat_s` only** → `storage-c$(t(tt)) − res-value$(ord=card)` | MS 1, profit **11025.0** — **MATCH ✅** |

**Conclusion:** the objective-gradient fix in `stat_s` is necessary **and sufficient** for robert; the `stat_x` head-offset index is a non-issue. This also explains why robert matches only via the `--nlp-presolve` warm-start (Day-0 bucket `model_optimal_presolve`): warm-started at 11025 it stays there, but cold it converges to the spurious 6741.67 admitted by the mis-emitted `stat_s`.

### 1.5 Why the harness (and the banked diagnosis) mis-localized to `stat_x`

`kkt_residual.py` warm-starts the multipliers with the presolve emit's **same-index** transfer `nu_sb.l(r,tt) = sb.m(r,tt)`. The NLP stores `sb.m` at the **head** labels (r,2),(r,3),(r,4), so the same-index load shifts `nu_sb` by one. That shift corrupts the residual of *both* `stat_x` and `stat_s`, and `stat_x(high,3)` happened to carry the largest *relative* residual (rel 7.2) — so the harness's top-5 were all `stat_x`, and the Day-12 quick classification concluded "the `stat_x` cross-term is wrong." The self-contained cold solve (§1.4) cuts through the transfer artifact and pins the true bug in `stat_s`. **This is the PR24 lesson in action: the banked fix-surface was a hypothesis, and the Day-0 re-trace corrected it.**

### 1.6 robert fix-surface hypothesis (Day-0, PR24 — to re-confirm in-sprint)

The bug is in the **objective-gradient → stationarity emit for `s`**, not the head-offset builder. Two coupled defects:
1. A **subset-domain objective term** (`storage-c(r)·s(r,t)`, `t(tt)` a subset of `tt`) is emitted into `stat_s` **without its `$(t(tt))` guard**.
2. A **fixed-literal-index objective term** (`res-value(r)·s(r,"4")`) is **dropped** from the stationarity of `s(r,"4")`.

Likely surface: the objective-gradient path (`src/ad/gradient.py` `find_objective_expression` / the per-variable gradient builder in `src/kkt/stationarity.py`) — the **same family as the Sprint-29 Day-3 #1447 maxmin fix** (objective-term scoping over a subset), extended to handle fixed-literal-element terms. **NOT** the head-offset builder (`stationarity.py:5562`/`:5750`). Blast-radius note for Task 9: the "terminal stock valued at res-value" (`s(r,"last")`) pattern is common in inventory/dynamic models — the fix must be checked corpus-wide.

---

## 2. mine — the actual (unchanged) head-domain-offset bug

mine's bug is firm from `ISSUE_1443` Day-6/7 and is a **different class** from robert's:

- Constraint: `pr(k,l+1,i,j)$c(l,i,j)..  x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)` — a head offset (`l+1`) **coupled with parameter offsets** (`li(k)`/`lj(k)`) on the tail indices.
- Day-7 experiment: hand-fixing **Site 2** (the dual transfer → `pr.m(k,l+1,i,j)`) and evaluating at the NLP optimum **clears the `nw` direction** (`li=lj=0`) but leaves **`ne`/`se`/`sw`** (parameter offsets active) at **~1e10 `comp_pr` infeasibility**. So mine's residual is in the **`comp_pr` precedence complementarity**, driven by the `l+1` head-offset × `li(k)`/`lj(k)` parameter-offset interaction — a **constraint-Jacobian** re-derivation across the three normalized sites (`comp_pr` emission, the dual transfer, the `stat_x` cross-term), **not** an objective-gradient term.

mine is a convex LP (monotone LCP): no Case-c escape — a correct emit must cold-solve; the cold `x → 4e10` is the `comp_pr` LCP residual.

---

## 3. Three-site coordination — recast per the findings

The prompt's "3-site index-map coordination" (`comp_pr` / `_emit_nlp_presolve` / `stat_x`) applies **only to mine**. robert needs no site coordination at all (a single objective-gradient site; cold-confirmed at 11025 with the `stat_s` fix alone).

**mine (the genuine head-domain-offset architecture):**

| Site | File:line (Day-0 trace) | Role for the head×parameter-offset map |
|---|---|---|
| Site 1 — `comp_pr` head var | cold `mine_mcp.gms:106`; gate at `src/kkt/stationarity.py:5750` | The `l+1` head + `i+li(k)`/`j+lj(k)` tail offsets in the precedence body — the site Day-7 proved still infeasible for offset directions. |
| Site 2 — `--nlp-presolve` dual transfer | `src/emit/emit_gams.py:1281` (`lam_pr.l = abs(pr.m)`) | Must read `pr.m` at the `l+1` head **and** drop `abs()` (sign-check vs the `nu`-class flip). Day-7: fixing this alone clears only `nw`. |
| Site 3 — `stat_x` cross-term | `src/kkt/stationarity.py:5562-5570` (landed #1224) | `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` — present; must stay consistent with Sites 1–2. |

The design requirement for mine: a **single head-offset index-map helper** that all three sites call, parameterized by (head-offset δ on `l`, parameter offsets `li(k)`/`lj(k)` on `i,j`), so the base↔head correspondence is applied identically everywhere. This is the emit-architecture work. There is **no shared code path with robert** (robert's fix is in the objective-gradient emit, a disjoint surface).

---

## 4. Cold-LCP consistency (Unknown 1.3)

- **robert: ✅ CONFIRMED.** After the `stat_s` objective-gradient fix, the cold MCP solves to MS 1 at 11025.0 — a clean convex-LP cold solve, **no warm-start needed**, no residual bound coupling. robert's cold LCP is fully consistent once the objective gradient is correct.
- **mine: hypothesis (firm).** The head-offset `comp_pr` fix must drive the `comp_pr` LCP residual (the `x → 4e10`) to 0. mine is convex ⇒ no Case-c escape ⇒ a residual after the 3-site fix would be a remaining emit/index-map bug (still Case-b), not non-convexity — continue the trace, do not REPLAN to warm-start.

---

## 5. Priority-1 re-scope + budget (feeds Task 5 gate + Task 6 REPLAN + Task 10 schedule)

**Unknown 1.1 verdict: ❌ does NOT generalize — robert and mine are DIFFERENT bug classes.** P1 splits into two independent tracks:

| Track | Bug class | Fix surface | Risk | Budget | Delta |
|---|---|---|---|---|---|
| **robert** (genuine-floor +1) | objective-gradient boundary-term (subset-guard drop + fixed-literal-element drop) | objective-gradient emit (`gradient.py` / `stationarity.py`), #1447 family — **NOT** the head-offset builder | **LOW** — cold-confirmed fix (11025), self-contained, tightly gateable | **~2–4 h** | +1 genuine floor (methodology → genuine cold) |
| **mine** (+1 Solve) | constraint-Jacobian head-offset × parameter-offset coupling in `comp_pr` | the 3-site head-offset index-map re-derivation (Sites 1–2–3) | **HIGH** — multi-site, Day-7 REPLAN-prone; each site may expose the next (Unknown 1.2) | **~10–16 h** | +1 Solve (model_infeasible → model_optimal) |

**Implications:**
- The robert genuine-floor gain is **de-risked and decoupled** — it should land early and independently (it does not wait on, or share code with, the head-offset architecture). Recommend scheduling robert as a standalone early-sprint objective-gradient fix (Task 10).
- mine remains the **REPLAN-prone** head-domain-offset architecture track (Task 6): PROCEED if the coordinated 3-site `comp_pr` fix drives the cold LCP to MS 1 within ~10–16 h; REPLAN mine (not robert) to a Sprint-31 head-offset-architecture workstream if each fixed site exposes the next. robert lands regardless.
- **The Sprint-30 Priority-1 title ("Head-Domain-Offset Emit Architecture … converts mine + robert") is now known to be a mischaracterization of robert** — Task 5 (gate refresh) and Task 10 (schedule) should record robert as an objective-gradient fix, and the head-offset architecture as mine-only.

---

## 6. Unknowns resolved

- **1.1 (robert → mine generalization): ❌ WRONG.** Different bug classes (robert = objective-gradient boundary-term; mine = `comp_pr` head×parameter-offset). No shared fix. Favourable: robert decouples + de-risks.
- **1.2 (3-site budget / each-site-exposes-next): mine-only.** The 3-site coordination is mine's; robert is a single objective-gradient site (no coordination). mine's 3-site risk stands (Day-7).
- **1.3 (cold-LCP consistency): robert ✅ confirmed** (cold 11025); **mine hypothesis** (the `comp_pr` fix must clear `x → 4e10`; convex ⇒ no Case-c).
- **1.4 (robert `nu_sb(r,tt+1)` cross-term + residual → 0): ❌ WRONG.** The hand-derived `nu_sb(r,tt+1)` is **not** robert's fix (control: `stat_x` patch → still 6741.67); the emitted `nu_sb(r,tt)` is already correct. The residual → 0 / cold-match (11025) is achieved by the `stat_s` objective-gradient fix instead.

---

## Appendix — evidence

- Harness: `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/robert.gms` → **CASE_B**, dual-transfer CONSISTENT, max `stat_x(high,3)` rel 7.20 (the transfer-artifact rows, §1.5).
- Cold-solve experiments (§1.4): GAMS on `/tmp` copies of `data/gamslib/mcp/robert_mcp.gms` — baseline 6741.67; `stat_x`-patch 6741.67; `stat_s`-patch **11025.0** (= NLP ref, DB `nlp_objective`).
- Hand-derivation (§1.3): NLP solve of `robert.gms` + per-row residual eval; corrected `stat_s(r,4)` residual → 0.
- mine: `docs/issues/ISSUE_1443_*.md` Day-6/7 (the `comp_pr` head×parameter-offset finding; Site 1–2–3 `file:line`).
- No `src/` or golden change committed; all probes reverted.
