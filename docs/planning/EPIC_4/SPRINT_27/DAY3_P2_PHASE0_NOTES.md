# Sprint 27 Day 3 — Priority 2 (#1381 Pattern C Phase B) Phase 0 hand-derivations

**Status:** 🟢 COMPLETE — camcge (5 of 5 consolidation variants) + cesam2 (B-3 dim-mismatch, incl. ROWSUM companion) fully hand-derived. Ready for Day 4 implementation.
**Date:** 2026-06-03
**Anchor commit:** `8f755328` (main; post-P1 #1398)
**Issue:** `docs/issues/ISSUE_1381_pattern-c-phase-b-redesign-plain-alias-and-dim-mismatch.md`
**Targets:** camcge (#1354) + cesam2 (#1355). `Alias (i,j)` in camcge; variables `dk(i)`, `xd(i)`, `p(i)` 1-D over i.

---

## Phase 0 baseline (current main emit, regenerated `8f755328`)

camcge is **path_syntax_error** (`$141`×2 + `$257`; 4 error markers). The #1398 (Phase A) gate does NOT fire on camcge because its alias-Sums have **no `$`-condition** — `_find_pattern_c_alias_sum` requires `expr.condition is not None`. So camcge falls through to the **standard offset-groups path**, which emits the consolidation as a **phantom-offset enumeration**: ~20 guarded terms per multiplier (40 for prodinv).

Example — current `stat_dk(i)` (the nu_ieq cross-term, **wrong/over-enumerated form**):

```
stat_dk(i).. pk(i)*nu_prodinv(i)
   + ((-1)*imat(i,i))*nu_ieq(i)
   + (((-1)*imat(i-1,i))*nu_ieq(i-1))$(ord(i) > 1)
   + (((-1)*imat(i+6,i))*nu_ieq(i+6))$(ord(i) <= card(i) - 6)
   + … [20 phantom-offset nu_ieq(i±N) terms, N = −10..+10] … =E= 0;
```

Per-multiplier phantom-offset counts (Phase B consolidation targets): nu_ieq 20, nu_inteq 20, nu_actp 20, nu_pkdef 20, **nu_prodinv 40** (B-2 case).

---

## The consolidation rule (hand-derived; the Phase 0 invariant)

For a source alias-Sum `eq(i).. … sum(j, COEFF · var(j)) …` where `j` is `Alias(i,j)` (canonical `i`), the stationarity cross-term in `stat_var(i)` consolidates to:

> **`sum(j, ±COEFF' · nu_eq(j))`**, where `COEFF'` is the source `COEFF` with its **argument positions preserved**, but the **sum-index slot rewritten to the stat/var-domain index `i`** and the **eq-domain-index slot rewritten to the alias `j`**; the multiplier `nu_eq(j)` is **alias-indexed**.

This is *not* the Phase A `alias↔eq_dom` swap — Phase A erases the coefficient's positional info via element-to-set (`imat(i,j)→imat(i,i)`) BEFORE the swap, then swaps to `imat(j,j)` (both coords wrong + `j` unbound). Phase B must build `COEFF'` **directly from the source body** (positions intact). [ISSUE_1381 §Root Cause]

---

## camcge — 5 consolidation variants (KU 2.1 Phase 0)

### B-1 (simple plain-alias) — 4 variants

**1. `ieq(i)..  id(i) =e= sum(j, imat(i,j)*dk(j));`  → stat_dk(i)** (the **nu_ieq** cross-term, primary Day 3 deliverable)

∂L/∂dk(i) from ieq: each ieq-instance `j'` contributes `nu_ieq(j')·∂ieq(j')/∂dk(i)`; in `sum(j, imat(j',j)*dk(j))` the dk(i) term is `j=i`, coeff `−imat(j',i)`. Sum over `j'`, rename `j'→j` (alias):

```
stat_dk(i):  sum(j, (-imat(j,i)) * nu_ieq(j))
```
Source `imat(i,j)` [eq-slot `i` first, sum-slot `j` second] → `imat(j,i)` [eq-slot→`j`, sum-slot→`i`]. ✅ matches ISSUE_1381 table.

**2. `inteq(j)..  int(j) =e= sum(i, io(j,i)*xd(i));`  → stat_xd(i)** (nu_inteq)

(inteq's own domain index is written `j` in source = canonical `i`; sum index `i`, var `xd(i)`.) ∂inteq(j')/∂xd(i) = `−io(j',i)`:

```
stat_xd(i):  sum(j, (-io(j,i)) * nu_inteq(j))
```

**3. `actp(i)..  px(i)*(1-itax(i)) =e= pva(i) + sum(j, io(j,i)*p(j));`  → stat_p(i)** (nu_actp)

Source coeff `io(j,i)` [sum-slot `j` first, eq-slot `i` second]. ∂actp(i')/∂p(i) = `−io(i,i')` → rename i'→j:

```
stat_p(i):  sum(j, (-io(i,j)) * nu_actp(j))
```
Note the **opposite arg orientation** to ieq — because here the sum-index is `io`'s *first* arg (→`i`) and the eq-index is the *second* (→`j`): `io(i,j)`. The rule still holds positionally.

**4. `pkdef(i)..  pk(i) =e= sum(j, p(j)*imat(j,i));`  → stat_p(i)** (nu_pkdef)

Source coeff `imat(j,i)` [sum-slot `j` first, eq-slot `i` second]. ∂pkdef(i')/∂p(i) = `−imat(i,i')` → rename:

```
stat_p(i):  sum(j, (-imat(i,j)) * nu_pkdef(j))
```

### B-2 (eq-domain factor OUTSIDE the inner Sum) — 1 variant

**5. `prodinv(i)..  pk(i)*dk(i) =e= kio(i)*savings - kio(i)*sum(j, dst(j)*p(j));`  → stat_p(i)** (nu_prodinv)

The inner sum `sum(j, dst(j)*p(j))` is multiplied by `kio(i)` **outside** the sum. ∂prodinv(i')/∂p(i): residual has `+kio(i')·sum(j, dst(j)*p(j))`, so ∂/∂p(i) = `kio(i')·dst(i)`. `dst(i)` is constant in `i'` → factor it out of the multiplier sum; rename i'→j:

```
stat_p(i):  dst(i) * sum(j, kio(j) * nu_prodinv(j))
```
- `dst(i)` — **var-side factor** (depends on the stat index `i`): stays OUTSIDE the new Sum.
- `kio(i')→kio(j)` — **eq-side factor** (depends on the eq-domain index): moves INSIDE, reindexed to the alias.
- `nu_prodinv(j)` — alias-indexed. ✅ matches ISSUE_1381 §Phase B-2.

→ The Phase B builder must factor the equation body as `<var-side> · <eq-side> · sum(alias, …)` BEFORE consolidating (ISSUE_1381 §B-2 `_classify_eq_body_factors`).

---

## cesam2 — dim-mismatch second anchor (B-3) — ✅ FINALIZED (Day 4)

**Set relationships (cesam2.gms):** `Set i` (SAM accounts); `ii(i)` = strict **subset** (`ii(i)=yes; ii("Total")=no;` — all accounts except Total); `Alias (i,j), (ii,jj)` → `j` aliases full set `i`, `jj` aliases the **subset** `ii`. So **`jj ⊆ i` confirmed** → the `$(jj(j))` guard is real. Variable `TSAM(i,j)` is 2-D (canonical `(i,i)`); `COLSUM(jj)` is 1-D → dim-mismatch.

**`COLSUM(jj)..  sum(ii, TSAM(ii,jj)) =e= Y(jj);`  → stat_tsam(i,j)**

∂COLSUM(jj')/∂TSAM(i,j): in `sum(ii, TSAM(ii,jj'))` the TSAM(i,j) term needs `ii=i` (sum picks it) AND `jj'=j` (the COLSUM instance). Both collapse — `ii=i` is bound by stat_tsam's 1st domain index, `jj'=j` selects the single COLSUM instance. So:

```
stat_tsam(i,j):  … + nu_COLSUM(j)$(jj(j)) + …      (NO outer Sum)
```
- multiplier `nu_COLSUM(j)` indexed by `var_dom[binding_position=1] = j`;
- subset guard `$(jj(j))` (COLSUM's domain `jj ⊆ i`);
- suppress the spurious `sameas`-block guards element-to-set emits under dim-mismatch. [ISSUE_1381 §B-3]

**Companion (same builder): `ROWSUM(ii)..  sum(jj, TSAM(ii,jj)) =e= Y(ii);`  → stat_tsam(i,j):  `nu_ROWSUM(i)$(ii(i))`** — binds TSAM's **position 0** (`i`), guard `$(ii(i))`. (SAMCOEF/TSAMEQ reference `TSAM(ii,jj)` directly with no inner Sum → ordinary diagonal terms, not Pattern C.)

**B-3 builder rule:** when `len(var_domain) != len(eq_domain)`, infer the binding position from the source body's variable reference (position of the eq-domain index in `TSAM(ii,jj)`), build `MultiplierRef(nu_eq, (var_dom[binding_pos],))`, apply the subset guard if the eq-domain set is a strict subset, and emit NO outer Sum.

---

## Phase 0 status: ✅ COMPLETE (camcge 5 variants + cesam2 B-3). Ready for Day 4 implementation.

---

## Phase 0 verification specs (for the Day 4 PR — per-term greps on regenerated camcge_mcp.gms)

```bash
# B-1 consolidated single-Sum forms present (and phantom-offset enumeration gone):
grep -c 'sum(j, ((-1) * imat(j,i)) * nu_ieq(j))'   camcge_mcp.gms   # ieq  → expect 1
grep -c 'sum(j, ((-1) * io(j,i)) * nu_inteq(j))'   camcge_mcp.gms   # inteq→ expect 1
grep -c 'sum(j, ((-1) * io(i,j)) * nu_actp(j))'    camcge_mcp.gms   # actp → expect 1
grep -c 'sum(j, ((-1) * imat(i,j)) * nu_pkdef(j))' camcge_mcp.gms   # pkdef→ expect 1
# B-2:
grep -c 'dst(i) * sum(j, kio(j) * nu_prodinv(j))'  camcge_mcp.gms   # prodinv → expect 1
# Regression — no phantom-offset enumeration + no Phase-A mis-swap:
grep -oE 'nu_(ieq|inteq|actp|pkdef|prodinv)\(i[+-][0-9]+\)' camcge_mcp.gms | wc -l   # expect 0
grep -c 'imat(j,j)' camcge_mcp.gms                                   # expect 0 (Phase-A mis-swap)
# GAMS compile clean (camcge leaves path_syntax_error → +1 Solve / +1 Match):
gams camcge_mcp.gms action=c lo=2  # expect 0 error markers
```
