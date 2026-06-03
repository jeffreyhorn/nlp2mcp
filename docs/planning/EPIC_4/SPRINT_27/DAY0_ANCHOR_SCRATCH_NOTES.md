# Sprint 27 Day 0 — Anchor KKT Hand-Derivation Scratch Notes

**Status:** 🟡 IN PROGRESS — 2 of 8 anchors derived (launch + qdemo7) on Day 0; remaining 6 (ferts, sambal, ganges, sroute, turkpow, dinam ×2 sub-shapes) continue Day 1 per PLAN.md §5.
**Anchor commit:** `148662a5`
**Purpose:** Phase 0 acceptance-gate input (PR20) for Priority 1 #1398 gate-predicate tightening. Hand-derive the expected post-fix KKT cross-term shape on each anchor BEFORE editing `src/kkt/stationarity.py::_find_pattern_c_alias_sum` (`stationarity.py:378`). Day 1/2 regenerates each `*_mcp.gms` and grep-verifies it matches the shape derived here.
**Cross-ref:** `PRIORITY_1_ANCHOR_MAPPING.md` §3 (launch), §4.1 (qdemo7).

---

## Anchor 1 — launch `stat_iweight(s)` / `stat_pweight(s)` (byte-stability anchor)

**Role:** NOT in the 15 #1398-affected cohort. launch is the Sprint 26 PR #1379 Phase A fix target; the Sprint 27 #1398 tightening must keep launch's emit **byte-identical** to Sprint 26 Day 13 final (KU 4.2). It is the regression canary, not a recovery target.

**Source constraint** (`data/gamslib/raw/launch.gms:86`):

```gams
dweight(s)..  weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss)) + instweight + pl;
```

`ge(ss,s)` is the order-relation alias indicator (stage `ss` at or above stage `s`); multiplier `nu_dweight(k)` for constraint instance `k`.

**Hand-derivation of ∂L/∂iweight(s):**

Lagrangian term (equality, written `weight(k) − RHS = 0`):
```
L ⊃ − Σ_k nu_dweight(k) · Σ_{ss : ge(ss,k)} ( iweight(ss) + pweight(ss) )   + …
```
`iweight(ss)` matches the stationarity variable `iweight(s)` only when `ss = s`, present iff `ge(s,k)`:
```
∂L/∂iweight(s) ⊃ − Σ_k nu_dweight(k) · 1$(ge(s,k))
              = − Σ_{ss : ge(s,ss)} nu_dweight(ss)        [rename constraint index k → emit's bound index ss]
              = sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss))
```

**Expected emit (matches `launch_mcp.gms` L276 / L279 — confirmed against `PRIORITY_1_ANCHOR_MAPPING.md` §3):**

```gams
stat_iweight(s).. … + sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss)) + … =E= 0;
stat_pweight(s).. … + sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss)) + … =E= 0;
```
`pweight(ss)` appears identically inside `dweight`, so `stat_pweight(s)` carries the same cross-term.

**Byte-stability invariants the #1398 tightening must preserve:**
1. **Order-relation indicator** `1$(ge(s,ss))` — distinct from set-membership indicators (`sc`, `ppos`, `ri`, `xb`); the tightened gate predicate must still accept `ge(s,ss)` as a valid Pattern C trigger.
2. **Multiplier uses the bound alias index `ss`** (`nu_dweight(ss)`), NOT the eq index `s` — semantically correct (`−Σ_{k≤s}` of the cumulative dweight constraint). The gate must NOT propagate the eq index into the multiplier here.
3. Index swap source→emit: `ge(ss,s)` → `ge(s,ss)` is correct (stationarity index `s` takes the former iweight-summation role; multiplier index `ss` takes the constraint-index role).

**Day 1 gate (per §3):** `grep -n 'sum(ss, ((-1) \* 1\$(ge(s,ss))) \* nu_dweight(ss))' launch_mcp.gms` → **2 matches**; full-file byte-diff vs Sprint 26 Day 13 final → **0 diffs**.

---

## Anchor 2 — qdemo7 `stat_xcrop(c)` (Pattern C; +1 firm Solve / +1 firm Match recovery)

**Role:** Primary Phase A overreach recovery target. compare_match at Sprint 26 Day 0 → regressed to path_syntax_error post-PR #1379. The Sprint 27 fix is verified by qdemo7 returning to compare_match.

**Source constraint** (`data/gamslib/raw/qdemo7.gms:177`, indicator decl `sc(s,c)` @ L27):

```gams
plow(s)..  sum(c$sc(s,c), xcrop(c)) =l= sum(r, xlive(r))*hpa + thire(s);
```

`≤` inequality indexed by `s`; multiplier `lam_plow(s) ≥ 0`. Indicator argument order is **`sc(s,c)`** (season `s` first, crop `c` second).

**Hand-derivation of ∂L/∂xcrop(c):**

```
L ⊃ Σ_s lam_plow(s) · ( Σ_{c : sc(s,c)} xcrop(c) − Σ_r xlive(r)·hpa − thire(s) )
∂L/∂xcrop(c) ⊃ Σ_s lam_plow(s) · 1$(sc(s,c))
            = Σ_{s : sc(s,c)} lam_plow(s)
            = sum(s, 1$(sc(s,c)) * lam_plow(s))
```

**Expected post-fix emit (BOTH bugs fixed):**

```gams
stat_xcrop(c).. … + sum(s, 1$(sc(s,c)) * lam_plow(s)) + … =E= 0;
```

**Current Sprint 27 Day 0 BUGGY emit (`qdemo7_mcp.gms` L240):** `sum(s, 1$(sc(c,s)) * lam_plow(c))` — TWO compounding Phase-A over-consolidation errors:
- **(a)** indicator arg order swapped: `sc(c,s)` instead of source-matching `sc(s,c)`;
- **(b)** multiplier leaks the eq-domain index: `lam_plow(c)` instead of bound-index `lam_plow(s)`.

`lam_plow` is declared over `s`; emitting `lam_plow(c)` is an out-of-domain reference → GAMS PATH compile error → path_syntax_error.

**Day 1/2 gate (per §4.1) — expect-present + 3 expect-absent (catches partial fixes):**
```bash
grep -n 'sum(s, 1\$(sc(s,c)) \* lam_plow(s))' qdemo7_mcp.gms   # expect 1 (correct)
grep -n 'sum(s, 1\$(sc(c,s)) \* lam_plow(c))' qdemo7_mcp.gms   # expect 0 (current buggy)
grep -n 'sum(s, 1\$(sc(c,s)) \* lam_plow(s))' qdemo7_mcp.gms   # expect 0 (partial: mult fixed only)
grep -n 'sum(s, 1\$(sc(s,c)) \* lam_plow(c))' qdemo7_mcp.gms   # expect 0 (partial: indicator fixed only)
```

**Predicate-signature takeaway for the Day 1 prototype:** the tightened `_find_pattern_c_alias_sum` must, for a Pattern C alias-sum derived from a `sum(c$sc(s,c), x(c))`-shaped constraint body, (i) preserve the **source indicator argument order** (do not transpose `sc(s,c)`→`sc(c,s)`) and (ii) bind the multiplier to the **constraint/summation index** (`s`), not the stationarity eq index (`c`). egypt (→ qdemo7, §5) is the 2-region extension and should fall out mechanically.

---

## Day 1 continuation queue (6 remaining anchors)

| Anchor | Shape | Source ref | Open Q |
|---|---|---|---|
| ferts | `stat_z(p,i)` multi-bound-index Pattern C, `ppos(i,p)` 2-set + outer `$(ppos(p,i))` guard | §4.2 | OQ5 (vs qdemo7 collapse) |
| sambal | `stat_x(i,j)` `__kkt1` synthetic alias + `xb(i,i__kkt1)` param-as-cond, **eq-index** mult `nu_cbal(i)` (correct) | §4.3 | OQ5 (vs launch collapse) |
| ganges | `stat_pls(r)` 4 inner alias-sums `ri(i,r)` + outer existential `$(sum(i,1$(ri(r,i))))` | §4.4 | gangesx mechanical follow |
| sroute | `stat_x(i,ip,ipp)` **unwrapped** Pattern C (no sum), `darc(ip,ipp)` + `(not sameas(i,ipp))` guard | §4.5 | OQ3 (harker map) |
| turkpow | `stat_zt(m,v,b,t)` two `__kkt` aliases, `vs(t__,t__)` self-loop + `bs(bp,b)` + sameas-Cartesian | §4.6 | OQ2 (shale sub-shape) |
| dinam | Shape A `stat_ka(te)` row-mult-collapse `lam_mb(i,t)` + `ts2(te,te)` self-loop; Shape B `comp_mb(i,t)` pre-collapse | §4.7 | OQ4 (1 shape or 2?) |

Open Questions 1–5 (`PRIORITY_1_ANCHOR_MAPPING.md` §6) resolved during Day 1/2 hand-derivation.

---

# Day 1 (2026-06-02) — remaining 6 anchors + the #1398 tightening

## The #1398 root cause + fix (binding)

**Empirical trace of `_find_pattern_c_alias_sum`** (`src/kkt/stationarity.py`) on qdemo7 vs launch:

| model | gate fires as | `canonical(alias)` vs `canonical(eq_dom)` | verdict |
|---|---|---|---|
| launch | `alias=ss, eq_dom=s` | `s == s` (SAME — `Alias(s,ss)`) | swap valid |
| qdemo7 | `alias=c, eq_dom=s` | `c[crop] ≠ s[season]` (DIFFERENT) | swap INVALID — mangles |

The Sprint 26 Phase A gate over-reached: it fired on **cross-set** alias sums and applied a blanket `alias↔eq_dom` swap (`_apply_pattern_c_swap_to_term` → `_rewrite_subset_to_superset`, which rewrites BOTH `SetMembershipTest` conditions AND `MultiplierRef` indices). For qdemo7 this transposed the source condition arg order AND the multiplier index, turning the **correct naive** emit `sum(s, 1$(sc(s,c)) * lam_plow(s))` into the **buggy** `sum(s, 1$(sc(c,s)) * lam_plow(c))`.

**Fix (committed prototype):** in `_find_pattern_c_alias_sum`, only return a match when `_resolve_alias_target(alias_name) == _resolve_alias_target(eq_domain_index)` (genuine self-alias of a single set, the launch shape); otherwise fall through to the recursive descent. The swap then fires only where it is mathematically valid.

**Verification:** qdemo7 fixed; launch + sambal + sroute + turkpow + all 11 Tier 0/1 canaries **byte-identical**; ferts/ganges/dinam corrected to source-order shapes (below). **KU 1.3 ✅** (gate fires on launch-shape self-aliases only).

> ⚠️ **Doc caveat (resolved OQ2/OQ3/OQ5; Day 2 update):** `PRIORITY_1_ANCHOR_MAPPING.md` §4 is *inspection-based, not formal* — the grep "expected" shapes for **ferts §4.2** and **ganges §4.4** were transcribed from the **buggy gate-mangled baseline** (wrong arg order + eq-index leak), so they asserted the WRONG shape. (**qdemo7 §4.1 was already correct** — it documents the Day 0 bug explicitly and expects the *fixed* `sc(s,c)`/`lam_plow(s)` shape.) The formal hand-derivations below give the correct (source-order) shapes; **§4.2 and §4.4 were corrected on Day 2** (2026-06-03).

## Anchor 3 — ferts `stat_z(p,i)` (CHANGED → corrected)

Source (`ferts.gms`): `ppos(p,i)` declared `(p,i)` (L297); `z(p,i)`; `mb(c,i).. sum(p$ppos(p,i), a(c,p)*z(p,i)) - … =g= 0`; `cc(m,i)$mpos(m,i).. sum(p$ppos(p,i), b(m,p)*z(p,i)) =l= util*k(m,i)`.

∂mb(c,i)/∂z(p,i) = `a(c,p)$ppos(p,i)` (the p'=p term), multiplier **`lam_mb(c,i)`** (i matches z's domain). Likewise cc → `b(m,p)$ppos(p,i) · lam_cc(m,i)`.

**Correct emit:** `… 1$(ppos(p,i)) … * lam_mb(c,i)` and `… * lam_cc(m,i)` — **source-order `ppos(p,i)`, multiplier index `i`** (NOT `ppos(i,p)`/`lam_mb(c,p)` as §4.2 claimed). ✅ matches my fix's output.

## Anchor 4 — sambal `stat_x(i,j)` (byte-stable — same-set self-alias)

Source: `Alias(i,j)`; `cbal(j).. t(j) =e= sum(i$xb(i,j), x(i,j))`; `rbal(i).. t(i) =e= sum(j$xb(i,j), x(i,j))`. ∂rbal(i)/∂x(i,j) collects via a synthetic alias `i__kkt1` of `i` (avoids GAMS "set under control"). `nu_cbal(i)` uses the **eq-domain index i — correct** (cbal is indexed by the balance set; the multiplier is genuinely eq-indexed). alias `i__kkt1` and eq_dom `i` are the **same set** → gate fires (correctly), emit unchanged: `sum(i__kkt1, ((-1) * 1$(xb(i,i__kkt1))) * nu_cbal(i))`. ✅ byte-stable.

## Anchor 5 — ganges `stat_pls(r)` (CHANGED → corrected)

Source: `ri(r,i)` declared `(r,i)` (L45); `pls(r)`; 4 constraints `qdep(i)/values(i)/firsts(i)/yself(i)` each containing `sum(r$ri(r,i), pls(r)·…)`. ∂qdep(i)/∂pls(r) = `ls(i)·depl(i)$ri(r,i)` (the r'=r term), multiplier `nu_qdep(i)`.

**Correct emit:** inner condition **`ri(r,i)` (source order)**, NOT `ri(i,r)` as §4.4 claimed. ✅ matches my fix (`ri(r,i)`, 45 occurrences). Outer existential guard `$(sum(i, 1$(ri(r,i))))` preserved.

## Anchor 6 — sroute `stat_x(i,ip,ipp)` (byte-stable — unwrapped Pattern C)

Source: `Alias(i,ip,ipp)`; `nb(i,ip)$(not sameas(i,ip)).. sum(ipp$darc(ipp,ip), x(i,ipp,ip)) =g= sum(ipp$darc(ip,ipp), x(i,ip,ipp)) + 1`. ∂[RHS sum]/∂x(i,ip,ipp) = `darc(ip,ipp)`, multiplier `lam_nb(i,ip)`, guarded by the eq's `(not sameas(...))`. No wrapping Sum (the matching ipp is the eq's 3rd index). Emit `(1$(darc(ip,ipp)) * lam_nb(i,ip))$((not sameas(i, ipp)))` ✅ byte-stable (the relevant indices are all the eq's own — no spurious cross-set swap).

## Anchor 7 — turkpow `stat_zt(m,v,b,t)` (byte-stable — order-relation self-alias)

Source: `Alias(t,v),(b,bp)`; `vs(t,v) = (ord(t) >= ord(v))` and `bs(b,bp) = (ord(b) >= ord(bp))` — **order relations on aliased sets** (structurally launch's `ge` family). The `t__kkt1`/`t__kkt2` synthetic aliases are aliases of `t` (=`v`), so `vs(t__kkt,t__kkt)` self-loops are **same-set** → gate fires (correctly), byte-stable. Both `__kkt` aliases, both self-loop indicators, and `bs(bp,b)` present (2/2/2 per grep). ✅

## Anchor 8 — dinam `stat_ka(te)` (CHANGED → corrected; 1 logical shape, resolves OQ4)

Source: `Alias(te,tep)`; `ts2(te,tep)` time-summation matrix. Two sub-features:
- **`ts2(te,te)` self-loop** (te/tep same set) — same-set → unaffected, byte-stable part.
- **`comp_mb(i,t)` cross-term** `bk(i,"agri",t)·ka(t)` → ∂/∂ka(te): the gate previously **leaked te into `lam_mb`** (cross-set over-reach: bound indices `i,t` vs eq index `te`). My fix stops it → **row-multiplier-collapse** `sum((i,t), (bk(i,"agri",t) * lam_mb(i,t))$(t(t)))` with both indices bound, no `te` leak. ✅ matches §4.7.

**OQ4 resolved:** dinam is **1 logical shape with 2 positional variations** (the self-loop ts2 part is byte-stable; the row-mult-collapse part is the single thing the tightening corrects). No separate gate-predicate input.

## Day 1 verification summary

| Anchor | Δ vs baseline | Correct per hand-derivation? |
|---|---|---|
| launch | byte-stable | ✅ (KU 4.2 anchor preserved) |
| qdemo7 | changed | ✅ `sc(s,c)`/`lam_plow(s)` |
| ferts | changed | ✅ `ppos(p,i)`/`lam_mb(c,i)` |
| sambal | byte-stable | ✅ `nu_cbal(i)` eq-index correct |
| ganges | changed | ✅ `ri(r,i)` source order |
| sroute | byte-stable | ✅ unwrapped, eq-own indices |
| turkpow | byte-stable | ✅ order-relation self-alias |
| dinam | changed | ✅ row-mult-collapse, no te leak |
| **11 Tier 0/1 canaries** | byte-stable | ✅ zero regressions |

**Day 2 (2026-06-03) — DONE:** corrected `PRIORITY_1_ANCHOR_MAPPING.md` §4.2 (ferts) + §4.4 (ganges) grep specs to the source-order shapes (qdemo7 §4.1 was already correct); regenerated the full 15-model #1398 cohort + launch through the pipeline for bucket-provenance (see SPRINT_LOG Day 2). **Remaining for the P1 PR:** PR14 + PR20 cross-reference, open PR.
