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
