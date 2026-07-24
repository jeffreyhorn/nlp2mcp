# Sprint 35 — fawley #1111/#1112 Constraint-Index-Diagonal Correction + Forcing Hand-Off Design (Priority 3)

**Prep Task:** 8 (High) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (KKT/emit specialist)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `483e7a7b` (`main` at the S35 prep Task-7 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/design only — re-confirms the gap + the H-b finding live (Task 2's re-measurement requirement), characterizes the constraint-index diagonal as a predicate, designs the leak-free guard + the `/tmp` control + the 2-D-cohort harness + the fawley fixture, specifies the forcing hand-off, and names the REPLAN exit. **No `src/` change.**

> **Disposition: a genuine, shippable correctness fix — but zero in-sprint bucket (H-b), and the fix surface is high-blast-radius shared machinery.** The design delivers **two separable things** and keeps them separate: (1) a leak-free constraint-index-diagonal `sameas` correction that drives `max|stat_bq| → 0` (a genuine cross-term fix, +1 genuine floor **only if** fawley cold-matches); and (2) the forcing hand-off for fawley's **+Solve**, which is **not** an in-sprint P3 deliverable — fawley is **H-b** (the MCP solves MS-5 even with the warm residual closed), re-confirmed and *strengthened* by this task's live re-measurement.

---

## Executive summary

fawley's `stat_bq(c,cf)` over-sums the `qsb`/`pbal` cross-terms: the `mbal` term correctly guards `$(sameas(cfq__,cf))`, but the `qsb`/`pbal` terms sum over `cfq__` **without** the diagonal guard. The fix adds `$(sameas(cfq__,cf))` to those two terms. This is a **constraint-index diagonal** — distinct from the #1049 guard (which fires when the *variable* has more dims than the constraint) — and it lands in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`, ~1430 lines), the most-patched function in the KKT emit, shared with the 2-D cohort (cesam2, camcge, ps2/ps3 family, polygon).

**Live re-measurement (Task 2 required it — the S34 P4 change moved fawley's warm point; fawley is MAXIMIZE, so P4's sense-aware transfer is directly in play):**

| Quantity | S34 record | This task (live, 2026-07-24) |
|---|---|---|
| verdict | CASE_B (emit_bug) | **CASE_B — unchanged** |
| dual scale | 486 | **486 — unchanged** |
| dual transfer | CONSISTENT | **CONSISTENT — unchanged** |
| `stat_bq(res-arab-l,fuel-oil)` | rel 0.973 / raw 473 | **rel 0.973 / raw 473 — unchanged** |
| **max-residual row** | `stat_bq(...)` | **`stat_trans(tr-2)` rel 1.00 / raw −488 — NEW** |

**The new finding sharpens, not contradicts, the S34 picture.** `stat_trans(tr).. sum(c, at(c,tr)*nu_mbal(c)) - piL_trans(tr)` is **emit-correct** (a clean `∂mbal/∂trans` cross-term — no over-sum, no missing `sameas`). Its rel-1.00 residual is therefore a **genuine non-emit divergence** — which **strengthens H-b**: the warm KKT point fails even the emit-correct rows, so no emit fix makes fawley cold-match. Two consequences:

1. **The P3 gate must be scoped to `max|stat_bq| → 0`** (the emit-fixable rows), **not** the harness's global max residual — `stat_trans` stays nonzero regardless of the `sameas` fix. (This refines the S34 gate.)
2. **H-b is re-confirmed and strengthened.** fawley's +Solve is non-emit (the MCP diverges MS-5 @ 4399.557 vs LP opt 2899.25, and now an emit-correct row is the binding residual) → a P5 forcing hand-off, **not** an in-sprint P3 gain.

**The correctness fix is worth landing (if leak-free) for the genuine-floor lever; the +Solve is not P3's to deliver.**

---

## §1. Gap + H-b re-confirmation (Unknowns 3.1 baseline, 3.3)

### 1.1 The over-sum (emit gap), re-confirmed live

`data/gamslib/mcp/fawley_mcp.gms:238`:

```gams
stat_bq(c,cf)..
  ( sum(cfq__, (((-1)*1$(bposs(cfq__,c)))*nu_mbal(c))$(sameas(cfq__, cf)))                                   * mbal — HAS $(sameas(cfq__,cf)) ✓
  + sum((cfq__,l,s), ((prop(c,s)*sum(m$(ms(m,s)),char(c,m))*1$(bposs(cf,c))*nu_qsb(cfq__,l,s))$(cfq(cfq__)))$(specs(cfq__,l,s)))  * qsb — NO sameas ✗
  + sum((cfq__,m),   ((((-1)*(char(c,m)*1$(bposs(cf,c))))*nu_pbal(cfq__,m))$(cfq(cfq__)))$(cfm(cfq__,m)))     * pbal — NO sameas ✗
  - piL_bq(c,cf) )$(cfq(cf)) =E= 0;
```

Source (`fawley.gms`): `bq(c,cf)` is 2-D; `qsb(cfq,l,s)$specs(cfq,l,s).. sum(c$bposs(cfq,c), prop(c,s)*sum(m$ms(m,s), char(c,m)*bq(c,cfq)))…` and `pbal(cfq,m)$cfm(cfq,m).. q(cfq,m) =e= sum(c$bposs(cfq,c), char(c,m)*bq(c,cfq))`. Here **`bq`'s second index `cf` = the constraint's own index `cfq`**, so `∂qsb(cfq,·)/∂bq(c,cf)` is nonzero **only when `cfq = cf`** — the diagonal. The emit sums over **all** `cfq__` → over-count. The `mbal` term (which sums `bq` over its *second* index) already carries the diagonal `$(sameas(cfq__,cf))`; qsb/pbal (which sum `bq` over its *first* index `c`, with the constraint's own index in the stat position) do not. **`max|stat_bq|` = rel 0.973 / raw 473 (dual scale 486) — identical to S34.**

### 1.2 The re-measurement finding — `stat_trans` is now the max row (emit-correct → H-b strengthened)

`stat_trans(tr).. sum(c, at(c,tr)*nu_mbal(c)) - piL_trans(tr)` = `∂mbal(c)/∂trans(tr) = at(c,tr)` summed over `c` — **algebraically correct**, no over-sum, no missing guard. Its **rel 1.00 / raw −488** residual is therefore **not an emit bug**; it is a genuine dual mismatch at the warm KKT point. fawley is **MAXIMIZE** (`solve exxon maximizing profit`), so the S34 P4 sense-aware bound-transfer (`abs(var.m)` at the active bound) is directly in fawley's warm path — the most likely origin of `stat_trans(tr-2)` surfacing as the binding row is the P4-moved warm point on a degenerate infeasible solve (like mine's shifting secondary residuals, Task 6). **This is exactly the re-measurement Task 2 required** ("`fawley_mcp_presolve.gms` was P4-regenerated; re-measure the H-b figures rather than inherit them"): the emit gap (`stat_bq` 473) is intact, but the *global* residual picture now has an emit-correct row on top — confirming the H-b divergence is non-emit and scoping the P3 gate to `stat_bq`.

### 1.3 H-b, re-confirmed

Per S34 Day 5 (control-proven): the `sameas` correction gives `max|stat_bq|` **473 → 18.468**, where the **18.468 residue was the P4 cc-dist bound-transfer cell — shipped S34 Day 4**. So **on the current post-P4 tree the `sameas` fix alone should reach `max|stat_bq| → 0`** (the cc-dist cell is now handled), not 18.468 — a refinement the `/tmp` control (§5) verifies. But **fawley still solves MS-5 @ 4399.557** (LP opt 2899.25) with the warm residual closed — a **non-emit divergence** (LP convergence at fawley's scale), now corroborated by the emit-correct `stat_trans` residual. **fawley does not cold-match; the +1 genuine floor is contingent on forcing (P5), not an in-sprint P3 gain.**

---

## §2. The constraint-index-diagonal predicate (Unknown 3.2)

The diagonal is a **genuinely new pattern**, not covered by any existing guard. Expressed over the emit-time index structures:

> **Constraint-index diagonal:** a Jacobian cross-term where the constraint's **own** (non-summed) domain index occupies the **stat variable's non-summed (output) index position**, and the emit builds the term inside a `sum` over that shared index — so it must be guarded `$(sameas(<summed-constraint-index>, <variable-stat-index>))` to restrict to the diagonal.

For fawley: qsb is `nu_qsb(cfq__,l,s)`, the stat variable is `bq(c,cf)`, and `cfq__` (the constraint's own index) is summed while occupying `cf`'s position (`bq`'s non-summed index) → guard `$(sameas(cfq__,cf))`.

**Distinguished from the existing guards:**

| Guard | Locus | Fires when | fawley qsb? |
|---|---|---|---|
| **#1049** | `src/kkt/stationarity.py:7176` | `len(var_domain) > len(mult_domain)` — the **variable** has *more* dims than the constraint (fixed-literal indices) | **No** — qsb `(cfq,l,s)` is 3-D, `bq` is 2-D; the *constraint* has more dims (the opposite orientation) |
| **#1110/#1111** | the offset-group / fresh-alias machinery (`_get_or_create_fresh_alias:4496`) | the **variable**-index diagonal (a variable's summed index, e.g. mbal) | **No** — that is the mbal term, already guarded; qsb is the *constraint*-index diagonal |
| **constraint-index diagonal (NEW)** | to be added | the **constraint's own** index occupies the variable's stat position and is summed | **Yes** — this is the qsb/pbal case |

The `mbal` term is the **variable-index diagonal** (already handled); qsb/pbal are the **constraint-index diagonal** (new). The predicate must detect the constraint-own-index-in-variable-stat-position orientation and add the guard **only** there.

---

## §3. Guard design + placement + precedence (Unknown 3.2)

**Placement:** the diagonal predicate is added in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`), at the point where the qsb/pbal cross-terms flow through the #1104/#1111 offset-group / fresh-alias machinery. It must fire **after** the #1049 check (which handles the variable-heavier orientation, disjoint) and **not** perturb the #1110/#1111 variable-index-diagonal path (the mbal term).

**Precedence argument against each existing `sameas` path** (the leak risk — the function carries a dozen: #764/#767/#1049/#1104/#1110/#1111/#1112/#1131/#1224/#1306/#1351):

- **#1049** (`:7176`, `len(var_domain) > len(mult_domain)`): **disjoint by orientation** — qsb is constraint-heavier, #1049 is variable-heavier. The new predicate requires `len(mult_domain) ≥ len(var_domain)` **and** the shared-index-in-stat-position condition, so it cannot co-fire with #1049.
- **#1110/#1111** (the variable-index diagonal, mbal): **must not fire on qsb** — the new predicate keys on the *constraint's own* index in the variable's stat position, whereas #1110/#1111 key on the *variable's* summed index. The precedence rule: the new guard applies only when the summed index is a **constraint** domain index (not a variable domain index), so the mbal term (variable-summed) is untouched.
- **#1104** (dimension-mismatch, `:4503`): the qsb/pbal terms already route through the #1104 fresh-alias rename; the new guard is an **additional condition** on the emitted term, not a change to the alias machinery, so #1104's behaviour is preserved.

The precise predicate + insertion point is a **hypothesis to re-trace at implementation** (PR24) — the standing "prep fix-surfaces are wrong ~half the time" lesson applies doubly in a 1430-line shared function.

---

## §4. Leak-free requirement + 2-D-cohort regression harness (Unknown 3.2)

**Operational leak-free requirement:**
- **No `mbal` term may change** — the mbal cross-term (the variable-index diagonal) is already correct and must be byte-identical after the fix.
- **The 1-D core must be byte-identical** — polygon, ps2_s, ps3_s_gic (the S31 #1111/#1112 second-index landings) must not regress.
- **The 2-D indexed-cross-term cohort** must be byte-stable — every model that routes through the #1104/#1111 machinery.

**The regression set (goldens present on the tree):** `cesam2`, `camcge`, `ps2_f_s`, `ps2_s`, `ps3_s_gic`, `polygon` (+ fawley itself). `mbal`/`ps2` are not separate corpus models (mbal is a fawley equation; ps2 is the family root). The harness:
- `--resolve-changed --since-commit 78ceaead` must report **fawley as the only changed golden** — every cohort golden byte-identical (bucket-stable).
- Determinism ×3 `PYTHONHASHSEED {0,1,42}` on the new `fawley_mcp.gms` (PR12).
- A byte-diff of each cohort golden vs its committed version (the strict leak check — no `nu_*`/`lam_*` term added or removed on cesam2/camcge/ps2/ps3/polygon).

---

## §5. The pre-`src/` `/tmp` control (Unknown 3.1)

Before any `src/` change: apply the diagonal `sameas` guard to fawley's emitted `stat_bq` by hand in `/tmp`, re-run `kkt_residual.py`, and require:

- **`max|stat_bq| → 0`** (machine zero) — **not** the 96% partial (473 → 18.468). Post-P4, the 18.468 cc-dist residue is expected already handled (the cell shipped S34 Day 4), so the `sameas` fix alone should reach 0; the in-sprint `/tmp` control **will** verify this (not executed in this prep). `modelstat` asserted.
- **The gate is scoped to `max|stat_bq|`**, not the harness's global max residual (which retains the emit-correct `stat_trans` non-emit residual, §1.2).

> **DESIGN-SPECIFIED (not executed here):** the `/tmp` control's "→ 0" verdict is the in-sprint executed gate. This prep records the *baseline* (`max|stat_bq|` 473, live) and the *target* (→ 0); the executed closure is Day-N.

---

## §6. fawley 2-D second-index property fixture (Unknown 3.2, P7)

A synthetic fixture (the P7 catalog entry from Task 3, `shape_fawley_2d_second_index` or similar): a 2-D variable `v(a,b)` in a constraint `con(b, …)$…` whose own index `b` occupies `v`'s second (stat) position and is summed, asserting the emitted `stat_v(a,b)` carries `$(sameas(<summed>,b))` on the constraint cross-term. **Fail-before/pass-after** — synthetic and in-process (sub-second, the `test_ad_crossterm_shapes.py` pattern), landing **only with** the correction. Not written if P3 defers (the S34 discipline: a fixture lands with its fix).

---

## §7. Forcing hand-off — the +Solve is NOT an in-sprint P3 deliverable (Unknown 3.4)

fawley's +Solve is a **P5 `--force` forcing problem**, explicitly **excluded** from P3's in-sprint scope:

- **H-b (re-confirmed + strengthened, §1):** the MCP solves MS-5 @ 4399.557 (LP opt 2899.25) with the warm residual closed; the emit-correct `stat_trans` residual confirms the divergence is non-emit (LP convergence at fawley's scale, not a cross-term gap).
- **Forcing levers to survey (P5):** `--force {homotopy, multistart, optfile}` (`src/cli.py`; the `SPRINT_30/NONCONVEX_FORCING_SURVEY.md` methodology). Evidence that would make the +Solve reachable: a `--force` lever that drives the cold/presolve MCP to `model_optimal` @ 2899.25. Absent that, fawley stays `model_infeasible`.
- **The +1 genuine floor is contingent on a cold match** (which H-b precludes without forcing) — **not** a P3 gain. If the `sameas` correction lands and fawley later cold-matches via forcing, *then* it counts (classified per the PR25 genuine-vs-methodology definition); in-sprint P3 delivers **0 bucket**.

---

## §8. REPLAN exit + disposition (Unknown 3.2)

**In-sprint disposition (recommended): the correctness fix is landable IF the `/tmp` control passes and the 2-D cohort stays byte-identical — but it moves 0 bucket (H-b), so it is a low-priority correctness-only landing.** The design's own **gate-leak REPLAN exit** (`FAWLEY_CORRECTION_FORCING_DESIGN.md` §6):

- **REPLAN / DEFER** iff: the `/tmp` control does **not** reach `max|stat_bq| → 0`; OR **any** cohort golden (cesam2/camcge/ps2/ps3/polygon) or the mbal term changes (a gate leak = a correctness regression on currently-passing models); OR the predicate cannot be made precise enough to fire on qsb/pbal without misfiring. Then fawley's `sameas` correction defers again (a dedicated effort + the 2-D-cohort harness), with the constraint-index-diagonal now fully characterized + the fix surface examined — a de-risked hand-off.
- **Budget:** given P3 is 0-bucket (H-b) and both P1 (mine, Task 6) and P2 (sarf, Task 7) have already REPLAN'd/DEFER'd in prep, the freed budget concentrates on **P4** (the designated bucket mover). P3's correctness fix is worth landing *if cheap and leak-free*, but it is **not** a bucket lever and should not displace P4.

**This re-affirms the S33/S34 risk/reward call** (high blast radius on shared machinery for 0 in-sprint bucket), now with the H-b finding **re-measured** (not inherited) and *strengthened* by the emit-correct `stat_trans` residual.

---

## §9. Known Unknowns verified by this task

- **Unknown 3.1** — ✅ **VERIFIED (baseline); DESIGN-SPECIFIED (the "→ 0" closure).** The `stat_bq` over-sum gap is re-confirmed live (`max|stat_bq|` rel 0.973 / raw 473, dual scale 486, CASE_B — identical to S34). The `/tmp` control target `max|stat_bq| → 0` (not the 96% partial; post-P4 the 18.468 cc-dist residue is expected already handled) is specified; the executed closure is the in-sprint gate (DESIGN-SPECIFIED).
- **Unknown 3.2** — ✅ **VERIFIED.** The constraint-index diagonal is characterized as a predicate (constraint's own summed index in the variable's stat position), distinguished explicitly from #1049 (variable-heavier orientation, `:7176`) and #1110/#1111 (variable-index diagonal). The guard placement + precedence argument against each `sameas` path, the operational leak-free requirement (no mbal change; 1-D core byte-identical), and the 2-D-cohort regression harness (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon byte-identical + `--resolve-changed` GO) are specified. The fix surface is a labelled hypothesis.
- **Unknown 3.3** — ✅ **VERIFIED (H-b re-confirmed and STRENGTHENED).** Task-8 addendum to Task 2's Day-0 block: the live re-measurement (required because the P4 change moved fawley's MAXIMIZE warm point) confirms the stat_bq gap unchanged (473) **and surfaces a co-equal emit-correct `stat_trans(tr-2)` residual (rel 1.00 / raw −488)** — a genuine non-emit divergence that strengthens H-b and scopes the P3 gate to `max|stat_bq|`. fawley solves MS-5 @ 4399.557 (LP opt 2899.25) with the residual closed; the +Solve is non-emit → P5 forcing.
- **Unknown 3.4** — ✅ **VERIFIED (negative — no in-sprint floor gain).** Under H-b fawley does **not** cold-match, so the +1 genuine floor is **contingent on forcing (P5)**, not an in-sprint P3 deliverable. The `sameas` correction changes fawley's cold emit (a genuine cross-term fix), but fawley stays `model_infeasible` with or without it, so the correction is a **correctness-only landing with 0 bucket**; the floor credit accrues only if a `--force` lever later produces a cold match (classified per PR25).

**Handed to Task 10 (Phase-0 gate):** the `/tmp` control (`max|stat_bq| → 0`, scoped to stat_bq not the global max, `modelstat` asserted); the leak-free 2-D-cohort byte-identity gate; the +Solve explicitly out of scope (H-b). **Handed to Task 9 (P5 forcing/consultation):** fawley's +Solve is a `--force` survey (H-b non-emit divergence). **Handed to Task 11 (projection):** P3 = correctness-only, **0 in-sprint bucket**; +1 floor contingent on forcing; budget concentrates on P4.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 8
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
