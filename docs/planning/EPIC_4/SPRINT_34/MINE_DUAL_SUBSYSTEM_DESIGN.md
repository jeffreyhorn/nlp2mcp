# mine #1443 — Head-Offset Dual Subsystem: Design (Sprint 34 Prep Task 3)

**Created:** 2026-07-18 · **Owner:** Sprint 34 prep (KKT/emit specialist)
**Prep Task:** 3 (Priority 1 foundation) · **Priority:** Critical
**Anchors:** `SPRINT_33/DAY2_MINE_REPLAN.md` (H1 value-invariant, REPLAN H3) · `SPRINT_33/DAY1_PROGRESS_NOTES.md` §2–§3 (the validated residual decomposition) · `SPRINT_33/MINE_CROSSTERM_DESIGN.md` (the `c`-boundary classification, the cross-term-correct finding)

> **Disposition (prep):** this document turns the Sprint-33 REPLAN(H3) hand-off into a concrete **head-offset dual-subsystem design** — the mismatch characterization, the reconciliation hypothesis **H_dual**, a **reframed** pre-`src/` `/tmp` control gate, the fix surface as a Day-0-re-confirm hypothesis (PR24), the H3′ REPLAN exit, and the sizing. **No `src/` change** — the `/tmp` control is the Sprint-34 **Day-1** executed gate; here its PROCEED acceptance is a **specification**, not an executed result. P1 remains the sprint's **highest-REPLAN-prior track** (its banked premise was refuted twice — S32 `N`-derivation, S33 H1 value-invariance).

---

## 1. Day-0 re-confirm (the fingerprint still holds — live)

`scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms` on the live tree (2026-07-18):

```
verdict: CASE_B  — emit_bug
dual scale: 1.35e+04
dual transfer: CONSISTENT (max comp infeas 0, max equality residual 0)
max-residual row: stat_x(3,1,1)   rel = 2.37e+00  (raw -3.20e+04)
top: stat_x(3,1,1) 2.37 · stat_x(1,3,1) 1.07 · stat_x(4,1,1) 0.815 · stat_x(2,3,3) 0.741 · stat_x(3,1,2) 0.667
```

Identical to the S33 Day-0/Day-1 fingerprint. Day-0 bucket (Task 2 `BASELINE_METRICS.md`): mine `model_infeasible`, **cold MCP MS 5** — the cold solve genuinely fails, not merely a warm residual. `modelstat` asserted throughout; **`x.up=inf` BANNED** (the S31 measurement-error lesson).

**Emit-site facts re-confirmed on the live tree:**
- Emitted `stat_x` (`data/gamslib/mcp/mine_mcp.gms:103`):
  ```gams
  stat_x(l,i,j).. ( (-1)*((conc(l,i,j)*value/100 - cost(l))*1$(d(l,i,j)))
    + sum(k, lam_pr(k,l,i-li(k),j-lj(k))$(c(l,i-li(k),j-lj(k))) - lam_pr(k,l-1,i,j)$(c(l-1,i,j)))
    - piL_x(l,i,j) + piU_x(l,i,j) )$(d(l,i,j)) =E= 0;
  ```
- Body-keyed complementarity `comp_pr(k,l,i,j)$((c(l,i,j)) and (ord(l) <= card(l)-1))` (`mine_mcp.gms:106`).
- Builder: `src/kkt/stationarity.py::_try_build_param_offset_crossterm` (line **5712**, used at 5933) — the Issue-#1224 parameter-offset path (mine is the only corpus model with a non-`Const` `IndexOffset`, `li(k)`/`lj(k)`).
- **`head_domain_offsets` (the S31 IR foundation) is defined in `src/ir/parser.py` but is NOT referenced anywhere in `src/kkt/stationarity.py`** — mine's cross-term does not flow through it (`grep head_domain_offsets src/kkt/stationarity.py` → 0 hits). This is the load-bearing plumbing fact for Unknown 1.4.

---

## 2. H1 value-invariance re-confirmed — keying is the wrong lever (Unknown 1.1)

The NLP precedence constraint is **head-placed**: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)`, so its dual lives at the **head label** `pr.m(k,l+1,i,j)`. The `--nlp-presolve` transfer already reads the head-label dual and stores it at the **body** label: `lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))`.

Sprint 33 Day 2 ran the pre-`src/` control (`DAY2_MINE_REPLAN.md` §1):

| Hypothesis | nonzero residual rows | Finding |
|---|---|---|
| baseline (current emit) | **22** | the CASE_B warm residual (matches the harness) |
| **H1 head-label re-keying** | **22** | **IDENTICAL — `d_N = d_Nh1` row-for-row; value-invariant** |
| obj-sign flip (BANNED) | 11 | only halves; refuted 4×; breaks the cold emit |
| max-convention upper-bound transfer | 19 | closes only the 3 `x.m>0` rows; not the `c`-boundary |

**The keying-invariance principle:** because a body-keyed `lam_pr(k,l,·) = abs(pr.m(k,l+1,·))` holds exactly the value a head-keyed `lam_pr_head(k,l+1,·)` would hold, re-keying the multiplier **label** (H1) changes the complementarity *pairing* (a solve-structure change) but leaves the **`stat_x` warm-residual values byte-identical**. **A pure keying change cannot pass a warm-residual gate — the warm residual is invariant to it.** This is the central lesson Sprint 34 inherits, and it forces the reframed gate in §4/§5.

---

## 3. The dual-architecture mismatch, characterized (Unknowns 1.1, 1.3)

### 3.1 The residual is exactly the pit's top edge — 22 rows

Classified against `c` (`ord(l)+ord(i)≤card ∧ ord(l)+ord(j)≤card`, `card(l)=4`) and `d` (`≤card+1`), the wrong-sign rows sit on **two boundary strata** (`MINE_CROSSTERM_DESIGN.md` §2):

| Stratum | example rows | position |
|---|---|---|
| **`c`-boundary** (`ord(l)+ord(i)=card` or `ord(l)+ord(j)=card`) | stat_x(3,1,1) [max], stat_x(1,3,1), stat_x(1,3,2), stat_x(1,3,3) | the top edge where a precedence constraint originates |
| **`d\c` ring** (`=card+1`) | stat_x(3,1,2), stat_x(3,2,1), stat_x(4,1,1) | real `x` in `d` with **no** precedence constraint of its own (not in `c`) |

Interior rows have `N = 0`. The full nonzero set is **22 rows** (the Day-2 control count), materially broader than the banked "6 bound-active rows."

### 3.2 The max row, term-by-term (Day-1 decomposition, dual scale 1.35e4)

At `stat_x(3,1,1)` (`x` upper-bound-active, `x.m = 0` — the NLP puts the binding entirely into the precedence duals):

| Term | Value | Reading |
|---|---|---|
| `dbg_obj` | −16000 | objective gradient `(-1)(conc·value/100 − cost)` |
| `dbg_t1` (lead) | 0 | `i−li`/`j−lj` out of range at `i=j=1` → no lead term (correct) |
| `dbg_t2` (lag) | −16000 | `−sum(k, lam_pr(k,2,1,1)$c(2,1,1))` = `−Σ_k abs(pr.m(k,3,1,1))` |
| `dbg_bnd` | 0 | `piL=piU=0` everywhere (`x.m=0` ⇒ no bound multiplier) |
| **`dbg_N`** | **−32000** | obj + lag (both negative — they **add**) |

To close, the cross-terms must supply **+16000**; but the lag coefficient is structurally **−1** with `lam_pr ≥ 0` ⇒ the term is `≤ 0` (cannot be +16000 without the **banned** sign flip or a **structural** cross-term change the S33 re-derivation refuted), and `x.m = 0` ⇒ no bound multiplier can absorb the gap.

### 3.3 The mismatch, named — and why it is a *dual-architecture* gap, not a bug in the cross-term

The NLP KKT stationarity for `x(3,1,1)` (LP, constraint `g = x(2,·) − x(3,1,1) ≥ 0`, `∂g/∂x(3,1,1) = −1`, multiplier `λ = Σ_k pr.m(k,3,1,1) ≥ 0`): `∂f/∂x − λ·∂g/∂x = −16000 + λ = 0 ⇒ λ = 16000`. The emit builds the MCP stationarity term for this same appearance as `+λ·∂g/∂x = −λ` (min-convention `F(x) = ∂f + Σ λ ∂g`), i.e. `−16000`. **The head-placed precedence dual enters the two stationarity forms with opposite orientation at the boundary**, and because `x.m = 0` (degenerate) there is no bound multiplier to reconcile them. The result at the `d\c` ring is a residual whose sign would demand a **negative** bound multiplier — **infeasible in the MCP** (hence cold MS 5, not merely a warm residual).

This is a **head-offset dual-architecture mismatch**: the constraint is *declared* over the body domain `(k,l,i,j)$c(l,i,j)`, *head-placed* at `(k,l+1,i,j)`, and the MCP re-keys **both** `comp_pr` and `lam_pr` to the body label. Complementarity is self-consistent under that re-key, but the head-side variable `x(l+1,i,j)` — a real variable in `d` at the ring, with no originating precedence constraint of its own — receives cross-term contributions from boundary `lam_pr` instances whose complementary (bound-active) pairing sits at a **different** variable. It is not a mislabeled or missing cross-term term (the term is algebraically correct, verified from scratch in S33 §3) — it is *where the head-placed dual's complementarity is anchored*.

**LP framing (why this is closable in principle):** mine is an **LP**, so the NLP optimum *is* the MCP optimum — the same KKT system. The boundary rows exhibit **primal degeneracy** (`x` at a bound with `x.m = 0`) with the shadow value pushed into the precedence duals; the cold MCP fails because the emitted stationarity anchors those degenerate duals at the body label, where their orientation does not close the head-side variable's row. A correct **head-offset dual subsystem** must anchor the precedence dual's complementarity to the head-side variable so the boundary rows close — a *structural* (complementarity-pairing) change, not a keying or bound-transfer change.

---

## 4. H_dual — the head-offset dual-subsystem design (Unknowns 1.2, 1.4)

### 4.1 The reconciliation hypothesis

**H_dual: anchor the head-placed precedence dual's complementarity to the head-side variable.** Concretely, emit the precedence complementarity and its cross-term so that the dual `lam_pr` for constraint `pr(k,l+1,i,j)$c(l,i,j)` pairs structurally with the head-side variable `x(l+1,i,j)` (the `−x(l+1)` appearance) and contributes `+lam_pr` to the body-side variable `x(l,i+li,j+lj)` — **with the complementary slack anchored at the head label** `(k,l+1,i,j)` where the NLP stores `pr.m`, rather than re-keying the value to the body label while leaving the pairing at the body variable. This differs from the refuted **H1**: H1 re-labelled the multiplier but kept the body-variable pairing (value-invariant); **H_dual changes the complementarity anchor (the solve structure), which the warm residual is blind to but the cold solve is not.**

**Why the warm residual is the wrong diagnostic here (the reframed gate — the key design contribution).** Per §2, keying is value-invariant, so *no* reconciliation that only moves labels will move the warm residual `N`. A structural pairing change likewise leaves the warm-point term VALUES unchanged — but it changes which variable's row the dual closes, and therefore whether the **cold** MCP reaches a feasible stationary point. **The gate must therefore be the COLD MCP reaching MS-1 @ 17500 (`modelstat` asserted), not `N → 0` at the warm point.** This corrects the S33 §5 gate (which used `N → 0`, a target no keying could hit) and is the reason S33's H1/H2 could not pass — they were gated on an invariant quantity.

### 4.2 Fix surface (a Day-0-re-confirm hypothesis, PR24)

- **`src/ir/`** — carry a **head-label-indexed** multiplier domain for the precedence complementarity. The natural carrier is the S31 `EquationDef.head_domain_offsets` (`src/ir/symbols.py`), which already describes, per domain position, the head offset (`l+1`) that distinguishes the head label from the body label. It is **already consumed elsewhere in the emit/KKT layer** (`src/emit/emit_gams.py::head_offset_marginal_index_map` reads it; `src/kkt/complementarity.py` + `src/kkt/sqr_reformulation.py` pass it through) — but it is **not consumed by the stationarity cross-term path** (`src/kkt/stationarity.py`, 0 hits, §1). H_dual is the **first consumer in the stationarity cross-term path**, so the new work is *wiring the existing IR into `_try_build_param_offset_crossterm`*, not adding an IR capability from scratch.
- **`src/kkt/stationarity.py`** — `_try_build_param_offset_crossterm` (line 5712): build the cross-term against a **head-anchored** `lam_pr`, and emit the `comp_pr` complementarity at the head label `(k,l+1,i,j)` (paired to the head-side variable), reading the head offset from `head_domain_offsets` rather than re-inverting the body-keyed offset.
- **`src/emit/emit_gams.py`** — the `--nlp-presolve` dual transfer (`_emit_nlp_presolve`): transfer `pr.m(k,l+1,i,j)` to the **head-anchored** `lam_pr` label consistently with the new complementarity (no change in value — the change is structural).

All three are **hypotheses to discriminate with the `/tmp` control** (§5), not asserted fixes. The S27 lesson stands: prep-doc `file:line` is wrong ~4× — trace and re-confirm on Day 0/1 before editing.

### 4.3 What H_dual is NOT

- **NOT H1** (head-label *re-keying* with body pairing) — value-invariant, refuted S33 Day 2.
- **NOT a sign flip** on the objective gradient or the cross-term — BANNED, control-refuted 4×.
- **NOT a bound-multiplier transfer** — `x.m = 0` at the boundary; there is nothing to transfer (the max-convention variant closes only the 3 `x.m>0` rows, not the `c`-boundary; that gap is the separate P4 track).
- **NOT `x.up=inf`** — BANNED (the S31 measurement error: relaxing the bound produced 34 unmatched-variable errors and read the embedded LP, not the MCP).

---

## 5. The pre-`src/` `/tmp` control (PR24/PR27 gate) — Day-1 executed, spec here

Run **before** any `src/` change; assert `modelstat`; `x.up=inf` BANNED. **In this docs-only prep the PROCEED criterion is a specification, not an executed result.**

1. **Residual re-decomposition (re-confirm).** Re-run the Day-1 term-by-term `stat_x` decomposition **from the repo root** (the emit `$include` is repo-relative) to reproduce the 22-row `dbg_N` and confirm the max-row breakdown (obj −16000, lag −16000, bnd 0, N −32000). *Gate:* faithful reproduction (already re-confirmed at the harness level in §1).
2. **H_dual structural prototype.** Hand-edit `mine_mcp.gms` (+ `mine_mcp_presolve.gms`) so the precedence complementarity is **head-anchored** (`comp_pr` at `(k,l+1,i,j)` paired to `x(l+1,i,j)`; the `stat_x` cross-term built against the head-anchored `lam_pr`). *Gate (reframed):* the **cold** MCP reaches **MODEL STATUS 1 at profit 17500** (`modelstat=1` asserted) — **not** `N → 0` at the warm point (§4.1: the warm residual is keying-invariant and is the wrong diagnostic). Confirm the 22 boundary rows close in the *cold* solution and interior rows are unperturbed.
3. **No-regression probe.** Spot re-emit the other head-offset / `_try_build_param_offset_crossterm` corpus members (**srpchase** is the reference) + `--resolve-changed --since-commit 750803b2` **GO** before any `src/` change.

**PROCEED (H_dual)** iff probe 2 reaches cold MS-1 @ 17500 and probe 3 is clean; else **REPLAN (H3′)**.

---

## 6. Sizing + REPLAN exit (Unknown 1.5)

**18–24 h — upper half (~22–24 h)**, given P1 is a from-scratch dual subsystem whose banked premise was twice-refuted:
- `/tmp` residual re-decomposition + the H_dual structural prototype + the **cold-MS-1** gate (~5–7 h) — the Phase-0 control.
- Head-anchored precedence complementarity + cross-term emit + the `head_domain_offsets` IR plumbing (`_try_build_param_offset_crossterm`; `_emit_nlp_presolve`) (~10–14 h).
- Determinism ×3 + golden-staleness + `--resolve-changed` + the `shape12` head-offset regression fixture (~3–4 h).

**Front-load:** P1 runs Days 1–5 so the PROCEED/REPLAN decision lands by the **Day-5 checkpoint** (Task 9 rates P1 **High** REPLAN-prior; surfacing early frees ~14–18 h → P6/P7, exactly as S33 did on Day 2).

**REPLAN exit (H3′):** if the `/tmp` H_dual prototype cannot drive the **cold** MCP to MS-1 @ 17500 without perturbing interior rows or regressing srpchase — i.e. the boundary is a genuine dual-degeneracy the emit cannot deterministically reconcile — mine stays `model_infeasible`, **no `src/` shipped**, and P1 hands off to a later sprint (or to the PATH-consultation track, since an LP whose warm KKT point is not MCP-reconcilable is a candidate consultation question). The de-risked hand-off is this document + the Day-1 decomposition.

---

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **1.1** | ✅ **VERIFIED** | H1 head-label re-keying is **value-invariant** (S33 Day-2 control, 22→22 rows, `d_N=d_Nh1`); the live harness re-confirms the CASE_B fingerprint (`stat_x(3,1,1)` 2.37, dual CONSISTENT). The residual is a **head-offset dual-architecture mismatch** (the head-placed `pr.m(k,l+1)` enters `stat_x` with opposite orientation at the boundary; `x.m=0` degeneracy), **not** a keying or cross-term error. |
| **1.2** | 🔍 **DESIGN-SPECIFIED (control pending)** | H_dual (anchor the head-placed dual's complementarity to the head-side variable) is stated with a `file:line` fix-surface hypothesis. **Key correction:** the gate is the **cold** MCP reaching MS-1 @ 17500, **not** `N→0` at the warm point (the warm residual is keying-invariant, §2/§4.1). The `/tmp` prototype is the Sprint-34 **Day-1** executed gate — **not run in this docs-only prep**, so the empirical question "does H_dual reach cold MS-1?" stays open (INCOMPLETE until Day 1). |
| **1.3** | ✅ **VERIFIED** | The residual is exactly the pit's top edge — the **`c`-boundary** (`ord(l)+ord(i)=card`) + the **`d\c` ring** (`=card+1`), **22 rows** (broader than the banked 6); interior rows are 0. Closing all 22 in the **cold** solution = MS-1 @ 17500 is the gate. |
| **1.4** | ✅ **VERIFIED** | `EquationDef.head_domain_offsets` exists (field in `src/ir/symbols.py`, populated in `parser.py`) and is **already consumed in the emit/KKT layer** (`emit_gams.py::head_offset_marginal_index_map`; `kkt/complementarity.py`; `kkt/sqr_reformulation.py`) — but it is **unused by `src/kkt/stationarity.py`** (0 hits, re-confirmed live). It is the natural carrier for the head-label-indexed multiplier H_dual needs; H_dual is its **first consumer in the stationarity cross-term path** — so the new work is *wiring the existing IR into `_try_build_param_offset_crossterm`*, not an IR capability from scratch. |
| **1.5** | ✅ **VERIFIED** | **18–24 h, upper half (~22–24 h)** given the from-scratch dual subsystem; the H3′ REPLAN exit is pinned; front-loaded Days 1–5 so the decision lands by the Day-5 checkpoint (P1 High REPLAN-prior). |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 3 (design; no `src/`)
**Last Updated:** 2026-07-18 · **Owner:** Sprint 34 prep (KKT/emit specialist)
