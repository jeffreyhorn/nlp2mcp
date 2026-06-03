# Sprint 27 Day 3 — Priority 2 (#1381 Pattern C Phase B) Phase 0 hand-derivations

**Status:** 🟡 IN PROGRESS — camcge fully hand-derived (5 of 5 consolidation variants); cesam2 (dim-mismatch, B-3) identified + shape stated; full cesam2 derivation finalizes Day 4 per PLAN §6.
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

## cesam2 — dim-mismatch second anchor (B-3) — Day 4 finalize

`COLSUM(jj)..  sum(ii, TSAM(ii,jj)) =e= Y(jj);` — eq-domain 1-D `(jj,)` (canonical `i`); variable `TSAM` is **2-D** `(i,i)`. The alias-Sum iterator `ii` binds TSAM's **position 0**; the eq-domain `jj` binds TSAM's **position 1**. Correct consolidated form (NO outer Sum — the alias is already controlled by the stat-eq's own variable-domain index):

```
stat_tsam(i,j):  … + nu_COLSUM(j)$(jj(j)) + …
```
- multiplier `nu_COLSUM(j)` indexed by `var_dom[binding_position=1] = j`;
- subset guard `$(jj(j))` since `jj ⊆ i`;
- suppress the spurious `sameas`-block guards element-to-set emits under dim-mismatch (emit-formatting artifact). [ISSUE_1381 §B-3]

**Day 4:** read cesam2 source (`TSAM`/`COLSUM`/`jj` decls), confirm the binding-position inference + the `jj ⊆ i` subset, finalize the stat_tsam hand-derivation; then implement Phase B-1/B-2/B-3 per ISSUE_1381 §Files Involved.

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
