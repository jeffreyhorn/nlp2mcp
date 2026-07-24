# Sprint 35 — `$149` CES/LES `prod()` Product-Rule Stationarity AD Root Analysis + Uncontrolled-Index Cohort Catalog

**Prep Task:** 4 (Critical, on the critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (AD/KKT)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `f21e09a8` (`main` at the S35 prep Task-3 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/analysis only — reproduces `$149` live, hand-derives the correct cross-term, localizes the defect (as a labelled hypothesis), and catalogs the cohort. **No `src/` change.**

---

## Executive summary

The `$149` blocker on ganges/gangesx is a **product-rule stationarity AD bug**: differentiating the CES/LES term `prod(j, (pc(j)/pc00(j))**ac(j,r))` with respect to `pc(i)` emits a `body_derivative / body` factor that **references the product's bound index `j` outside the `prod(j, …)` scope**, where GAMS sees `j` as an uncontrolled set — **9 × `$149`, all on the single `stat_pc(i)` equation** (golden line 1002). The correct derivative is `prod(j, (pc(j)/pc00(j))**ac(j,r)) * ac(i,r) / pc(i)` — with `i`, the controlled stationarity index, and **no free `j`**.

Two findings materially **correct** the Sprint-34 carryforward framing, and both are the "verify per model — prep hypotheses are wrong ~half the time" discipline firing again:

1. **`$149` is a GAMS error *code*, not a single *root*.** The carryforward states the `$149` product-rule fix "gates six models (ganges/gangesx/dinam/indus/turkpow/clearlak)" and "unblocks the `$149` half of dinam/indus/turkpow/clearlak." Compiled and inspected per model, **only ganges and gangesx carry the product-rule `$149`** (on `stat_pc`, from the `prod` derivative). The `$149` markers on dinam / indus / turkpow / clearlak sit on **entirely different constructs** — a `sameas` alias-sum (`stat_v`), a raw data-assignment power term (`yc … ** gammafrt`), a lag-KKT sum (`stat_zt`), and a set/element data assignment (`tmp1 = sum(nn$leaf(nn), snprob(leaf))`) — that merely share the error number. **The product-rule fix helps ganges and gangesx only.**

2. **The cohort is far more multi-root than S34 recorded.** Per-model compile of the committed goldens shows dinam carries `$140/$8/$37/$171/$141` (not just `$140/$149`), indus carries `$141×8/$140/$130/$409/$148` (dominated by `$141`, not `$149`), turkpow is dominated by `$170/$171` (`$149×1`), and clearlak is dominated by `$352` (`$149×1`, and **not** `$171` as S34 stated). `$257` and `$300` are **cascades** (one per model, on the `Solve`/overflow line), not independent roots.

**Consequence for P4 and Task 11:** the product-rule `$149` fix, combined with Task 5's `$141`/`$145` fixes, is the path to recovering **ganges + gangesx** (both need all three roots — no model recovers from one). dinam/indus/turkpow/clearlak are **not** on that path; their `$149` markers are unrelated and their dominant blockers are untouched. The honest P4 target is **+2 (ganges, gangesx)**, not "+ the `$149` half of six models."

**Fix-surface hypothesis (labelled — verify at implementation):** the `_diff_prod` collapsed-form branch (`src/ad/derivative_rules.py:~3395`, Issue #1330's `symbolic_name_match` path) returns `expr * (body_derivative / expr.body)` and **delegates index-safety to the emitter's alias step** ("the emitter aliases the prod's bound to a fresh name … so the post-`*` term references the outer free index"). The emitter's `collect_index_aliases` (`src/emit/expr_to_gams.py:757`) renames a `Prod` bound only on collision with (1) the equation domain or (2) an *enclosing* Sum/Prod — **not** when the bound is referenced by a *sibling multiplicative factor*, which is exactly the collapsed derivative's shape. So `j` leaks free. This is an AD-emit **contract** defect spanning both files, not a one-line typo; Task 5 decides which layer to fix.

---

## §1. Reproduction (Unknown 4.3)

Emitted ganges live (`sys.setrecursionlimit(50000)`, `.venv/bin/python -m src.cli data/gamslib/raw/ganges.gms`) — the emit is **byte-identical** to the committed golden `data/gamslib/mcp/ganges_mcp.gms` (md5 `72c5d5f268e9dad458f61f58491872c5`), consistent with Task 3's determinism finding, so the committed golden is analysed directly. Compiled with `gams … a=c` (compile-only; GAMS 53).

**Error tally (ganges, from the GAMS listing):** `$141×15` · `$149×9` · `$145×3` · `$300×1` · `$257×1`.

**All 9 `$149` markers are on one equation** — `stat_pc(i)`, golden line 1002:

```
stat_pc(i)..  nu_pcdet(i) + sum(r, ((-1) * ch(i,r)) * nu_cpidet(r))
  + sum(j, sum(r, ((-1) * (pop(r) * ac(i+2,r) * (mc(r) - sum(j__, pc00(j__)*gamma(j__,r)))
      * prod(j__, (pc(j__)/pc00(j__))**ac(j__,r))                              ← prod renamed to j__ (chunk 1)
      * (pc(j)/pc00(j))**ac(j,r) * ac(j,r)/(pc(j)/pc00(j)) * 1/pc00(j)**1 / (pc(j)/pc00(j))**ac(j,r)))
    * nu_les(i,r)))
  + sum(r, (ch(i,r) - pop("rural") * (gamma(i,r)
      + ac(i,"rural") * (mc(r) - sum(j, pc00(j)*gamma(j,r)))
      * prod(j, (pc(j)/pc00(j))**ac(j,r))                                      ← prod NOT renamed (chunk 2)
      * (pc(j)/pc00(j))**ac(j,"rural") * ac(j,"rural")/(pc(j)/pc00(j)) * 1/pc00(j)**1 / (pc(j)/pc00(j))**ac(j,"rural"))
      + pop("rural") * ac(i,"rural") * (…) * prod(j, (pc(j)/pc00(j))**ac(j,r))
      * (pc(j)/pc00(j))**ac(j,"rural") * …)                                    ← same free-j factor again
    * nu_les(i,r))
  + …  =E= 0;
****   … $149 $149 $149 $149 $149 $149 $149 $149 $149 $300
```

**The offending index is `j`.** In **chunk 2**, `prod(j, (pc(j)/pc00(j))**ac(j,r))` binds `j` and then *closes its scope*; the factor that follows — `(pc(j)/pc00(j))**ac(j,"rural") * ac(j,"rural")/(pc(j)/pc00(j)) * … / (pc(j)/pc00(j))**ac(j,"rural")` — references `pc(j)`, `pc00(j)`, `ac(j,"rural")` with **`j` now free** (no enclosing `sum`/`prod` controls it). GAMS `$149` = *"Uncontrolled set entered as constant."* The nine markers land on the nine `j`-bearing tokens across the two additive occurrences of this factor.

**Why chunk 1 compiles but chunk 2 does not.** The same product-derivative appears twice, rendered by two different paths:
- **Chunk 1** wraps the whole term in `sum(j, …)` and renames the product's bound to `j__` (`prod(j__, …)`). Here `j` *is* controlled by the outer `sum(j)`, so no `$149` — though the term is still semantically wrong (it sums the derivative over `j`, and carries a spurious `ac(i+2, r)` offset; see §5.2).
- **Chunk 2** is the collapsed form `prod(j, …) * (derivative-factor)` with **no** `sum(j)` wrapper and **no** rename — so `j` is free → `$149`.

---

## §2. Hand-derived correct cross-term (Unknown 4.3)

The source equation (`data/gamslib/raw/ganges.gms:1012`):

```
les(i,r)..  pc(i)*ch(i,r) =e= pop(r)*( pc(i)*gamma(i,r)
              + ac(i,r)*(mc(r) - sum(j, pc00(j)*gamma(j,r))) * prod(j, (pc(j)/pc00(j))**ac(j,r)) );
```

Let `P(r) = prod(j, (pc(j)/pc00(j))**ac(j,r))`. Only the `j = i` factor depends on `pc(i)`, so via the logarithmic derivative:

```
log P(r) = sum(j, ac(j,r) * log(pc(j)/pc00(j)))
∂(log P)/∂pc(i) = ac(i,r) * (1 / (pc(i)/pc00(i))) * (1/pc00(i))
               = ac(i,r) * (pc00(i)/pc(i)) * (1/pc00(i))
               = ac(i,r) / pc(i)
```

therefore

```
∂P(r)/∂pc(i)  =  P(r) * ac(i,r) / pc(i)
             =  prod(j, (pc(j)/pc00(j))**ac(j,r)) * ac(i,r) / pc(i)
```

**Every index is bound: `j` by the `prod`, `i` and `r` by the stationarity equation `stat_pc(i)` / the enclosing `sum(r,…)`. No free index.** (Cross-checked numerically for a 2-element `j` set: `d/dpc₁ [(pc₁/a₁)^α₁ (pc₂/a₂)^α₂] = α₁/pc₁ · P`. ✓)

### Candidate emit forms

| # | Form | GAMS | Numerical safety |
|---|---|---|---|
| **1 (simplified — recommended)** | `P · ac(i,r)/pc(i)` | `prod(j, (pc(j)/pc00(j))**ac(j,r)) * ac(i,r) / pc(i)` | safest: divides by `pc(i)`, a strictly-positive price (bounded `> 0`) |
| **2 (prod-ratio — minimal mechanical fix)** | `P · f'(i)/f(i)` | `prod(j__, (pc(j__)/pc00(j__))**ac(j__,r)) * ( ac(i,r)*(pc(i)/pc00(i))**(ac(i,r)-1)/pc00(i) ) / ( (pc(i)/pc00(i))**ac(i,r) )` | divides by `f(i)=(pc(i)/pc00(i))**ac(i,r)` → unsafe as `pc(i)→0` |
| **3 (exp-sum-log)** | `exp(sum(j, ac(j,r)·log(pc(j)/pc00(j)))) · ac(i,r)/pc(i)` | as written | unsafe: `log(pc(j)/pc00(j))` needs `pc(j) > 0` for **all** `j` |

**Recommendation:** the correct value is the same for all three; the difference is index-binding and numerical safety. The **minimal correct fix** is form 2 — bind the derivative factor to the controlled stationarity index `i` (and alias the product bound to `j__`), so nothing references the product's dummy index free — which is exactly what chunk 1 *almost* does and chunk 2 fails to do. Form 1 is the cleaner target if the emit's power/division simplification can reach `f'(i)/f(i) → ac(i,r)/pc(i)`; it is also the numerically safest. Task 5 chooses; either eliminates the free `j`.

---

## §3. Defect localization (Unknown 4.3 — **hypothesis, per the standing lesson**)

> Prep `file:line` fix-surfaces are wrong ~half the time (S27–S34). The **symptom** below is certain (read from the emitted golden); the **surface** is a hypothesis with its supporting evidence, to re-trace at implementation.

**Certain (symptom):** the product-derivative factor on `stat_pc(i)` references the `prod` bound `j` outside the `prod` scope → free index → `$149`. The AD layer, not a cleanup pass, is the surface (contra the general "these live in `stationarity.py`" prior — this one is in the AD differentiation + emit-aliasing contract).

**Hypothesis (surface), two layers:**

1. **`src/ad/derivative_rules.py:_diff_prod` (~lines 3395–3405)** — the Issue-#1330 `symbolic_name_match` branch returns
   ```python
   log_term = Binary("/", body_derivative, expr.body)      # (df/dx)/f — references the prod bound
   return Binary("*", expr, log_term)                       # prod(...) * ((df/dx)/f)
   ```
   Its own comment states the contract it depends on: *"The emitter aliases the prod's bound to a fresh name (e.g. `i → i__`) … so the post-`*` term references the outer free index, not the prod's iteration."* So `_diff_prod` **emits a form that is only safe if a downstream aliasing step renames the prod bound** wherever the post-`*` factor references it.

2. **`src/emit/expr_to_gams.py:collect_index_aliases` (line 757)** — renames a `Prod` bound only on two conflicts: *"(1) Sum/Prod index collides with equation domain; (2) inner Sum/Prod index collides with outer Sum/Prod index (nested reuse)."* In the collapsed form `prod(j,…) * (…(j)…)`, the post-`*` factor is a **sibling multiplicative term**, not an enclosing binder and not the equation domain (`j ≠ i`), so **neither conflict fires, the bound stays `j`, and the sibling `j` is emitted free.** This is the failing link.

**Supporting evidence that the two layers are the surface:**
- Chunk 1 (general log path, `expr * sum(j, …)`) *is* aliased to `j__` and wrapped in `sum(j)` → compiles; chunk 2 (collapsed path, `expr * (…)`) is not → `$149`. The two paths differ exactly as the two branches of `_diff_prod` differ.
- The 18 other prod-in-stationarity models that compile (§5.1) are the **name-match** case (prod index == wrt index, e.g. camcge's #1330 `prod(i, cd(i)**cles(i))` w.r.t. `cd(i)`), where the collapsed form + the existing aliasing works. ganges is the **cross-index** case (prod over `j`, differentiate w.r.t. `pc(i)`, `j ≠ i`) — the case the aliasing contract does not cover.

**Open question for Task 5 (which layer):** (a) `_diff_prod` should not emit a form that references the prod bound outside the `prod` without itself aliasing/substituting it — e.g. use form 1/2 with the derivative factor rebound to the wrt index `i`; or (b) `collect_index_aliases` should detect a `Prod` bound referenced by a sibling factor and alias it. Option (a) is the more targeted (it fixes the mathematics at the source and yields the correct `ac(i,r)/pc(i)` shape); option (b) is broader and riskier (it changes aliasing for every collapsed prod-derivative). **Recommend (a).**

---

## §4. Cohort catalog (Unknowns 6.1, 6.2) — per-model, from live compiles

All seven committed goldens compiled (`gams … a=c`); distinct `$NNN` codes with counts. **`$149`-as-product-rule is marked `PR`; other `$149` are a different construct.**

| Model | `$NNN` × count (compiled) | product-rule `$149`? | dominant/independent roots | recovers on the `$149` PR fix alone? |
|---|---|---|---|---|
| **ganges** | `$141×15` · **`$149×9`** · `$145×3` · `$300×1`c · `$257×1`c | **YES — `stat_pc`, `prod(j,…)`** | `$141` (NaN-cleanup, Task 5) + `$145` (`*`-domain, Task 5) | **No** — needs `$141`+`$145`+`$149` (all three) |
| **gangesx** | `$141×15` · **`$149×9`** · `$145×3` · `$300×1`c · `$257×1`c | **YES — same `stat_pc` root** | identical to ganges | **No** — same three roots (verified independently) |
| **dinam** | `$140×5` · `$8×3` · `$149×3` · `$37×2` · `$171×2` · `$141×1` · `$257×1`c | **No** — `stat_v(jd,te)`, a `sum(j__,…)$(sameas(j__,jd))` alias-sum | `$140` (pruned-var `.l`-init) + `$8`/`$37`/`$171` | No — `$149` is 3 of ~13 markers, different construct |
| **indus** | `$141×8` · `$140×5` · `$130×4` · `$409×3` · `$149×3` · `$148×2` · `$767/$408/$36×1` · `$257×1`c | **No** — a raw data assignment `yc(…)=… **gammafrt(cfr)` | `$141` (dominant) + `$140` + `$130` + `$409` | No — heavily multi-root; **also allowlisted** (§4.4) |
| **turkpow** | `$170×6` · `$171×5` · `$149×1` · `$141×1` · `$257×1`c | **No** — `stat_zt(m,v,b,t)`, a lag-KKT `sum(t__kkt,…)` | `$170`/`$171` (domain violations, dominant) | No — `$149` is 1 of ~13 markers |
| **clearlak** | `$352×4` · `$141×2` · `$149×1` · `$257×1`c | **No** — `tmp1 = sum(nn$leaf(nn), snprob(leaf))` set/element assign | `$352` (dominant) + `$141` — **not `$171`** (S34 said `$171`; **wrong**) | No — `$149` is 1 of ~8 markers |
| **turkey** | `$161×6` · `$141×1` · `$257×1`c | **n/a — no `$149`** | `$161` (dotted-tuple set decl, its own root) | n/a — turkey is not a `$149` model |

`c` = **cascade** (`$257` "Solve not checked because of previous errors" appears once per model on the `Solve` line; `$300` "remaining errors not printed" is a per-line suppression marker). Neither is an independent root.

### Answer to "what still fails after a correct `$149` product-rule fix"

- **ganges / gangesx:** `$141×15` + `$145×3` remain → recover **only** with Task 5's `$141` + `$145` fixes *and* this `$149` fix, all three together. (Confirms S34: no model recovers from one root.)
- **dinam / indus / turkpow / clearlak:** **unchanged in practice** — their `$149` markers are unrelated constructs, and each is dominated by other independent roots (`$140`, `$130`/`$409`, `$170`/`$171`, `$352`). The product-rule fix removes 0–3 markers per model and recovers none.
- **turkey:** unaffected (no `$149`).

**This refutes the carryforward's "`$149` unblocks the `$149` half of dinam/indus/turkpow/clearlak."** For turkpow and clearlak the "`$149` half" is a single marker on an unrelated construct; for dinam and indus the `$149` is a minority of a heavily multi-root failure. The clean beneficiaries are **ganges and gangesx only.**

### 4.4 `indus` cannot serve as a golden-diff signal (from Task 3)

`indus` is in `scripts/sprint_audit/golden_staleness_allowlist.txt` for cross-environment byte non-determinism (#1461). Even if a fix touched its emit, its golden diff is suppressed. Verify indus (and any allowlisted cohort member) by **compile-error count**, not golden diff — and note its `$149` is a raw-data-assignment power term, not the product-rule root, so it is out of P4's `$149` scope regardless.

---

## §5. Blast radius + secondary observations

### 5.1 Regression set — models with `prod()` in stationarity that currently compile

20 committed goldens emit a `prod()` inside a `stat_*` row; **18 of them compile and solve** today (the CGE/methodology cluster + others), so they are the **regression set the P4 `$149` fix must not break**:

```
agreste  camcge  dyncge  etamac  hhfair  hhmax  irscge  korcge  lmp2
lrgcge   moncge  prolog  qdemo7  quocge  splcge  stdcge  twocge  weapons
```

(plus ganges/gangesx, the two that fail). These use the **name-match** product-derivative (prod index == wrt index) that the collapsed `_diff_prod` branch + existing aliasing handle correctly — including camcge, whose `prod(i, cd(i)**cles(i))` motivated the #1330 collapsed-form fix in the first place. The P4 change must fix the **cross-index** case (ganges) **without perturbing the name-match case** these 18 rely on: the Phase-0 gate (Task 10) must byte-compare all 18 goldens + `--resolve-changed` GO. `lmp2`'s `prod(p, y(p))` symmetric-optimum case (called out in the #1330 comment) is the most sensitive — include it explicitly.

### 5.2 Secondary artifacts on `stat_pc` (out of `$149` scope — flagged for Task 5)

Two further anomalies on the same `stat_pc(i)` line, **not** `$149` but worth banking:
- **`ac(i+2, r)`** in chunk 1 — a spurious `+2` index offset on the cross-sector term. A latent index-offset misattribution independent of the free-`j` bug; would produce a *wrong value* even once `$149` is fixed. Verify when the prod-derivative is corrected.
- **`… * 1 / pc00(j) ** 1 / (pc(j)/pc00(j)) ** ac(j,r)`** — the `** 1 /` precedence renders the `f'(i)/f(i)` factor as a malformed chain (the source of the single `$300` overflow marker). The correct simplified form (§2, form 1) eliminates it entirely.

Both are downstream of the same botched product-derivative emit; a correct form-1/form-2 rebuild should remove them, but Task 5 should confirm rather than assume.

---

## §6. Known Unknowns verified by this task

- **Unknown 4.3 (primary)** — ✅ **VERIFIED.** `$149` reproduced live on ganges (byte-identical golden); the offending `stat_pc(i)` line captured verbatim with the free `j` identified (§1); the correct cross-term hand-derived as `prod(j,(pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)`, fully index-bound, with three emit forms and a recommendation (§2); the defect localized to a **two-layer `file:line` hypothesis** (`derivative_rules.py:_diff_prod` collapsed branch + `expr_to_gams.py:collect_index_aliases`), labelled a hypothesis with its supporting evidence, and the distinguishing cross-index feature that isolates ganges/gangesx from the 18 working prod-models (§3, §5.1). The AD layer — not a cleanup pass — is the surface.
- **Unknown 6.1 (primary)** — ✅ **VERIFIED, and the S34 impact framing CORRECTED.** All seven cohort goldens compiled and catalogued by code × count (§4). **`$149` is a code, not a root: only ganges/gangesx carry the product-rule `$149`;** dinam/indus/turkpow/clearlak's `$149` markers are unrelated constructs and each model is dominated by other independent roots. "What still fails after `$149`" answered per model. The clean beneficiaries are **ganges + gangesx only** → the honest P4 `$149`+`$141`+`$145` target is **+2**, not six models.
- **Unknown 6.2 (primary)** — ✅ **VERIFIED.** The multi-root discipline is upheld and *extended*: the cohort is more multi-root than S34 recorded (dinam `$140/$8/$37/$171/$141`; indus `$141`-dominated; turkpow `$170/$171`-dominated; clearlak `$352`-dominated — **not `$171`**, correcting S34), `$257`/`$300` are cascades, and ganges/gangesx were verified **independently** (identical root sets confirmed, not inferred). No model recovers from a single root.

**Decision handed to Task 5 (recovery design):** specify the `$149` correction as form 1/form 2 at the AD layer (`_diff_prod`, option (a)), sequenced after `$141`/`$145`; gate it against the 18-model prod-in-stationarity regression set (lmp2 explicitly); and drop dinam/indus/turkpow/clearlak from the `$149` recovery expectation — they are P6 residual, not P4 `$149` beneficiaries. **Decision handed to Task 11 (projection):** P4's `$149`-path Solve target is **+2 (ganges, gangesx)**, contingent on all three roots landing together.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 4
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
