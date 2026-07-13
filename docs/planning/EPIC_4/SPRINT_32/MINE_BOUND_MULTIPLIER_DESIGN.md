# mine 4th Bound-Complementarity Site — Localization + Stationarity-Consistent Bound-Multiplier Design

**Created:** 2026-07-13
**Prep Task:** 3 (Priority 1 foundation)
**Issue:** #1443
**Status:** Design (prep) — the fix is designed here; the in-sprint P1 work implements + validates it behind the Phase-0 gate (Task 8).

**Objective:** Turn the Sprint-31 Day-3 REPLAN — the residual **4th bound-complementarity site** at bound-active `stat_x` rows — into a concrete **stationarity-consistent bound-multiplier design**, sizing the deepest Sprint-32 track before the schedule is set. All experiments below are read-only (harness runs + cold/presolve emits to `/tmp`); no `src/` change.

---

## §1. 4th-site localization (harness, current tree)

`kkt_residual.py data/gamslib/raw/mine.gms` reproduces the Sprint-31 Day-3 fingerprint **exactly** on the current tree:

```
model: mine    tol: 0.001 (relative)
dual scale: 1.35e+04
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 0.00e+00 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_x(3,1,1)   rel = 2.37e+00  (raw -3.20e+04)
```

| row | residual (raw) | relative |
|---|---|---|
| `stat_x(3,1,1)` | −32,000 | 2.37 |
| `stat_x(1,3,1)` | +14,500 | 1.07 |
| `stat_x(4,1,1)` | −11,000 | 0.815 |
| `stat_x(2,3,3)` | +10,000 | 0.741 |
| `stat_x(3,1,2)` | −9,000 | 0.667 |

**Reading:** the residual localizes **entirely to `stat_x` rows** (stationarity), with **dual-transfer CONSISTENT** (comp-infeasibility 0, equality-residual 0) — so the transferred `lam_pr` (head-shifted via the Site-2 `head_offset_marginal_index_map`) and the complementarity pairings are correct; the **stationarity does not balance at the NLP optimum**. This is the "4th site": with the correct head-shifted duals, `stat_x` still does not close. The residual magnitudes (~±10⁴, mixed sign) track the objective-coefficient scale `conc·value/100 − cost`, i.e. an **un-absorbed objective-gradient term**, not a scaling artifact.

---

## §2. Bound-dual mismatch characterization

### Model structure (`data/gamslib/raw/mine.gms`)

```gams
Positive Variable x;                 * x(l,i,j) 'extraction of blocks'  (x.lo = 0)
x.up(l,i,j) = 1;                     * so x is bounded [0, 1]
def..  profit =e= sum((l,i,j)$d(l,i,j), (conc(l,i,j)*value/100 - cost(l))*x(l,i,j));
pr(k,l+1,i,j)$c(l,i,j)..  x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);   * head offset δ=+1 on l; body offsets li/lj on i/j
```

mine is an **LP** (linear objective, linear precedence constraints, `x ∈ [0,1]`). `x` appears in the objective **only for `$d(l,i,j)` cells**; non-`d` cells are fixed (`x.fx$(not d)=0`) because their `stat_x` is vacuous.

### Emitted `stat_x` (cold + presolve, identical)

```gams
stat_x(l,i,j)..
  ( (-1)*((conc(l,i,j)*value/100 - cost(l)) * 1$(d(l,i,j)))
    + sum(k, lam_pr(k,l,i-li(k),j-lj(k))$(c(l,i-li(k),j-lj(k)))
             - lam_pr(k,l-1,i,j)$(c(l-1,i,j)))
    - piL_x(l,i,j) + piU_x(l,i,j) )$(d(l,i,j)) =E= 0;
```

Define the **non-bound part** `N(l,i,j)` = everything except the bound multipliers:

```
N(l,i,j) = (-1)*(conc·value/100 − cost)·1$d
           + sum(k, lam_pr(k,l,i-li,j-lj)$c(l,i-li,j-lj) − lam_pr(k,l-1,i,j)$c(l-1,i,j))
```

so `stat_x = N − piL_x + piU_x`, and closure requires **`piL_x − piU_x = N`**.

### The 4th site: the warm-start bound-multiplier transfer

The `--nlp-presolve` emit warm-starts the bound multipliers directly from the LP reduced cost `x.m` (`src/emit/emit_gams.py:1548–1577`, "Transfer variable marginals to bound multipliers"):

```gams
piL_x.l(l,i,j)$(abs(x.l(l,i,j) - x.lo(l,i,j)) < 1e-6 and x.m(l,i,j) > 0) =  x.m(l,i,j);
piU_x.l(l,i,j)$(abs(x.l(l,i,j) - x.up(l,i,j)) < 1e-6 and x.m(l,i,j) < 0) = -x.m(l,i,j);
```

**Why `piL_x/piU_x = x.m` does not close `stat_x`:** `x.m` is the LP solver's **reduced cost** = its own stationarity residual w.r.t. its own Jacobian/constraint-dual decomposition. At mine's **degenerate LP vertex** (many precedence constraints active simultaneously, and `x` at `{0,1}`), the reduced cost is **not uniquely split** between the bound and the active precedence constraints — the LP attributes some of the "push" to `x.m` that the emitted `stat_x` attributes to the head-offset-inverted `lam_pr` cross-term. So `x.m ≠ N` at those rows, and setting `piL_x/piU_x = ±x.m` leaves `stat_x = N − (±x.m) ≠ 0`. The harness confirms this precisely: the duals are CONSISTENT (`lam_pr`, `pr.m` correct), yet `stat_x` rel 2.37 — a **bound-complementarity ⊥ stationarity inconsistency** localized to the `x.m` transfer, not to `lam_pr` or the cross-terms.

---

## §3. The fix: stationarity-consistent bound-multiplier derivation

**Principle:** derive the bound multipliers **from the stationarity balance** (the residual `N` after the correct `lam_pr` transfer), **not** from the LP reduced cost `x.m`. Because `stat_x = N − piL_x + piU_x`, choose:

```
piL_x = max(N, 0)      piU_x = max(−N, 0)
```

This closes `stat_x` **exactly by construction** (`piL_x − piU_x = N`), and — since exactly one of `piL_x`/`piU_x` is nonzero — it respects the complementarity pairing (`piL_x ⊥ comp_lo_x = x − lo`, `piU_x ⊥ comp_up_x = up − x`). Its **sign must match `x`'s bound-active status** (a built-in consistency check): `N ≥ 0` ⇒ `piL_x ≥ 0` ⇒ `x` at its lower bound; `N ≤ 0` ⇒ `piU_x ≥ 0` ⇒ `x` at its upper bound; `N ≈ 0` ⇒ both ≈ 0 (interior). A sign that contradicts the active bound flags a deeper stationarity inconsistency (→ §4 REPLAN exit).

**Emit site (single, local):** `src/emit/emit_gams.py:1548–1577` — the "Transfer variable marginals to bound multipliers" block, **presolve-only**. Replace the two `± x.m`-keyed assignments with an `N`-residual-based assignment that (a) reads the already-transferred `lam_pr.l` + the objective coefficient to form `N(l,i,j)`, then (b) splits `N` by sign into `piL_x.l`/`piU_x.l`. The cold emit and the `stat_x`/`comp_*` equation bodies are **unchanged** (this is a warm-start-value change only).

**Scope / blast radius (Unknown 1.3 — favorable):** the change is confined to the presolve bound-multiplier **warm-start value** transfer. It does **not** touch the `EquationDef.head_domain_offsets` IR field or the Site-2 `head_offset_marginal_index_map` constraint-dual transfer (`src/emit/emit_gams.py:1354/1545`), which are a *separate* block. The head-offset foundation regression guard passes on the current tree:

```
pytest tests/unit/ir/test_head_domain_offsets.py \
       tests/integration/emit/test_head_offset_presolve_transfer.py \
       tests/unit/emit/test_head_offset_marginal_map.py  → 16 passed
```

The 5 head-offset models stay byte-stable; the cold `mine_mcp.gms` is unchanged (only `mine_mcp_presolve.gms`'s two transfer lines change). Because `x.m`→bound-multiplier transfer is a **generic** block (every bounded-variable model uses it), the in-sprint implementation must gate the `N`-derivation to the head-offset-coupled case (or verify byte-stability of the other presolve models via `--resolve-changed`) so it doesn't perturb non-mine presolve goldens.

---

## §4. Warm→cold residual gate + 5th-coupling REPLAN exit

**Protocol (Unknown 1.4 — the Day-2 measurement-error lesson):** assert `mcp_model.modelstat` (== 1) **before** reading any objective; never use the structurally invalid `x.up=inf` experiment (it produces 34 "Unmatched variable not free or fixed" errors and the "objective" read is the embedded `$include` LP, not the MCP).

**Gate (in-sprint P1, behind the Task-8 Phase-0 gate):**

1. **Warm residual → 0 (primary gate).** With the `N`-derivation transfer, re-run `kkt_residual.py data/gamslib/raw/mine.gms` → expect **Case-a** (`stat_x` residual ≈ 0; the warm point is a true KKT point). This is the direct test that the 4th site was the whole emit inconsistency.
2. **Presolve MS-1 (the +1 Solve).** Solve `mine_mcp_presolve.gms` (`modelstat` asserted) → expect **MODEL STATUS 1** (PATH starts at the now-consistent KKT point). mine's target is +1 Solve; the presolve solve is the deliverable.
3. **Cold MS-1 (stretch).** Solve cold `mine_mcp.gms` → MS-1 if PATH can navigate the degenerate LCP without a warm start; a cold-only failure (the LCP-degeneracy PATH struggles with even for a correct system) is **not** a 5th coupling — the presolve solve already lands the +1.

**5th-coupling REPLAN exit (Unknown 1.2):** REPLAN to a Sprint-33 deeper head-offset architecture **iff** the `N`-derivation does **not** reduce the **warm** residual to ≈ 0 — i.e. a fresh `stat_x` (or other-class) residual persists at the NLP optimum after the fix, or the sign of `N` contradicts the bound-active status at some row (indicating the emitted `stat_x` cross-term itself is still inconsistent, a genuine 5th site). In that case the P1 budget (~14–20h) reallocates to P6 (offset-alias generalization) + P7 (property catalog) per the Task-9 assessment; the head-offset IR foundation + Site-2 transfer + this bound-multiplier design remain the banked de-risked hand-off.

---

## §5. Summary + Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 1.1 | Can the bound-active `stat_x` be reconciled with a stationarity-consistent bound-multiplier? | ✅ VERIFIED — YES by construction: `piL_x = max(N,0)`, `piU_x = max(−N,0)` closes `stat_x = N − piL_x + piU_x`; the emit site is `src/emit/emit_gams.py:1548–1577` (presolve, local). |
| 1.2 | Single 4th site, or does a 5th coupling surface? | ✅ VERIFIED (design) — the residual is localized to the `x.m` bound-multiplier transfer (duals CONSISTENT); the in-sprint warm-residual→0 gate is the single decisive test, with the explicit 5th-coupling REPLAN exit if the warm residual does not close / the sign contradicts the bound. |
| 1.3 | Does the fix preserve the head-offset IR foundation (zero regression)? | ✅ VERIFIED — the change is confined to the presolve bound-multiplier warm-start value; independent of the Site-2 `head_offset_marginal_index_map`; the 16 head-offset guard tests pass; cold `mine_mcp.gms` byte-unchanged. Gate the `N`-derivation (or `--resolve-changed`-verify) so other presolve goldens stay byte-stable. |
| 1.4 | Does the warm→cold gate assert `modelstat`? | ✅ VERIFIED — the protocol asserts `mcp_model.modelstat` before every objective read; the `x.up=inf` experiment is recorded BANNED (34 unmatched-variable errors). |

**Decision: PROCEED** to the in-sprint P1 implementation of the stationarity-consistent bound-multiplier derivation (`src/emit/emit_gams.py:1548–1577`, presolve), behind the Task-8 Phase-0 gate (warm residual → 0 → presolve MS-1, `modelstat` asserted). The 4th site is precisely localized (the `x.m` transfer), the fix is a single local emit change, and the head-offset foundation is provably preserved. The 5th-coupling REPLAN exit is explicit.

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team (KKT/emit specialist)
**Evidence:** `kkt_residual.py data/gamslib/raw/mine.gms` (CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT); cold `/tmp/mine_mcp.gms` + presolve `/tmp/mine_mcp_presolve.gms` emits; `src/emit/emit_gams.py:1548–1577`; 16 head-offset guard tests green.
