# Sprint 31 — Day 0 Traces + Tractability Probes

**Day:** 0 (Kickoff)
**Date:** 2026-07-09
**Scope:** docs/trace-only — read-only parses/emits + the KKT-residual harness; the one committed artifact is `tests/fixtures/head_offset_ir_roundtrip.gms` (the P1 round-trip fixture, always-run test infra). No `src/` change.

---

## 1. Day-0 baseline confirmed = Sprint 30 final

`git diff ea4191dc..HEAD -- src/ scripts/` is **empty** → no `src/`/`scripts/` drift since the S30 close; **reuse the committed DB, no fresh retest**. The canonical-scope recompute reproduces the baseline exactly:

**Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 70) · model_infeasible 7 · Tests 4,997** (anchor `ea4191dc`, `BASELINE_METRICS.md`).

## 2. Day-0 traces (PR24) — each Phase-0 gate's fix-surface re-confirmed

| Track | Day-0 verdict (re-confirm) | Source |
|---|---|---|
| **mine** (P1) | **CASE_B**, `stat_x(4,1,1)` rel **1.33**, dual-transfer **CONSISTENT** | fresh `kkt_residual.py` run this Day 0 — byte-identical to the banked fingerprint |
| **polygon** (P2) | **CASE_B**, `stat_theta(i12)` rel **0.492**, CONSISTENT | Task 4 re-run (this sprint); the second-index drop is at `stationarity.py:5767` |
| **camcge** (P3) | S1 ✓ (`nu_equil` ×9 / `nu_lmequil` ×5 in the stationarity), S2 ✓ (no numéraire fixed); banked cold MS-4 singular | fresh emit this Day 0 + `ISSUE_1330` Day-11 |
| **hhfair** (P5) | `stat_u` = `(-1)·prod·ufact(t)/u(t)` (the inlined log-derivative gradient, no `nu_objective`) — **emit-correct** | fresh emit this Day 0 (Probe 3) |
| **rocket** (P6) | Case-c (clean emit at the NLP point; the failure is non-convergence, not an emit bug) | `NONCONVEX_FORCING_SURVEY.md` §2/§4 |
| **sarf** (P4) | emit exceeds a 2-minute wall clock / no golden (the translate_failure the P4 O(constraints) re-emit must avoid) | Task 8 timing |

## 3. Tractability probes — the three deepest tracks validated before the mid-sprint budget commits

### Probe 1 (P1 round-trip) — ✅ the head-offset field addition is FEASIBLE

Authored the committed fixture `tests/fixtures/head_offset_ir_roundtrip.gms` (mine-shaped: head `+1` on domain position `l` + body param offsets `li(k)`/`lj(k)`). A read-only parse confirms:
- `pr.has_head_domain_offset = True` (the bare bool today), `pr.domain = ('k','l','i','j')` (collapsed base — the `l+1` head dropped);
- the `l+1` head is present in the body RHS as `IndexOffset(base='l', offset=Const(1.0), circular=False)`, and the param offsets `li(k)`/`lj(k)` are preserved in the body LHS as `IndexOffset(.., ParamRef(..))`.

**→ the `head_domain_offsets` field addition (Day 1) is feasible** — the head δ + the param offsets are all recoverable from the parsed AST (the loss is only that `_domain_list_has_offset` collapses them to a bool). The full `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)` assertion becomes the **Phase-1 gate once the field lands (Day 1)**.

### Probe 2 (P3 dual-consistent) — ✅ approach validated; the MS-1 prototype is the Day-6 substantive experiment

The camcge `--nlp-presolve` MCP emits + compiles (657 lines). **S1 ✓** (the market-clearing duals `nu_equil`/`nu_lmequil` appear in the stationarity — dropping a market-clearing row orphans a needed price/wage), **S2 ✓** (no numéraire fixed — prices homogeneous degree 0). The banked Day-11 evidence stands: the **price-pin reaches the correct allocation omega 191.735 but stays MS-4** (the dual block is rank-deficient), and the naive drop-row corrupts (omega 299). **The approach is sound** (the premise + the dual-flaw are pinned). The full **dual-consistent redefinition → MS-1 at omega 191.7346** hand-prototype (keep every row + numéraire + the Walras dual redefinition, re-pairing first) is the **substantive P3 experiment, time-boxed to Day 6** per the design's prototype-on-`/tmp`-first plan (`CAMCGE_DUAL_CONSISTENT_DESIGN.md` §4) — it is the Day-6 PROCEED gate before the `src/` change.

### Probe 3 (P5 hhfair ν_objective) — ✅ hhfair is genuine Case-c → P5 pivots to the CGE cluster

A read-only emit confirms hhfair's `stat_u(t) = (-1)·(prod(t̄,u(t̄)**ufact)·ufact(t)/u(t)) + nu_utility(t) − piL_u(t)` — the **maximize-negated log-derivative product gradient**, emit-correct (no `nu_objective` — the objective is inlined). The ν_objective reduction is sign-equivalent for hhfair, and the Sprint-30 sign flip is refuted → **hhfair is genuine Case-c** (documented; **the sign flip stays BANNED**). **P5 pivots to the emit-fixable CGE cluster** (irscge/lrgcge/moncge `stat_xp` rel ~0.06, convex) for Day 10.

## 4. PR25 Day-0 tally

Genuine floor **70** / methodology **22** (as-measured Match 92). The **genuine-floor → ≥ 73 conversion map:** polygon [P2] +1 (coupled offset-alias) · hhfair — **no** (Case-c) → the **CGE cluster** [P5] +1 to +3 (`stat_xp` reduction) · mine [P1] +0 to +1 (if it cold-matches). **Honest projection (Task 7):** Solve ≥ 109 (needs mine [P1] + camcge [P3]) is the most REPLAN-sensitive KPI (P3 has a per-model-numéraire fallback that still solves; P1 does not); the genuine-floor ramp ≥ 73 is conditional on P2 + P3 + P5.

## 5. Day-0 disposition

**GO for Day 1.** All Phase-0 fix surfaces re-confirmed; the three tractability probes validate the deepest tracks (P1 field addition feasible, P3 approach sound, P5 hhfair Case-c → CGE-cluster pivot). One Day-0 scope note: the P3 dual-consistent MS-1 prototype is time-boxed to the Day-6 gate (the approach is validated; the definitive MS-1 confirmation is the substantive experiment). No `src/` change; the committed artifact is the P1 round-trip fixture.
