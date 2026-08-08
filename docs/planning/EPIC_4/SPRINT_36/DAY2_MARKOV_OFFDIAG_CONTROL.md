# Sprint 36 — Day 2: markov P1 Part-2 (`σ=sp`) Mechanism-C `/tmp` Control → REPLAN (emission PROVEN, gate leaks)

**Date:** 2026-08-07 · **Branch:** `planning/sprint36-day2-markov-offdiag` · **Scope:** `/tmp`-only control (scratch `src/` prototype, **reverted** — `src/kkt/stationarity.py` byte-identical to `main`); no `src/` ships, no golden change.

**Outcome: a decisive, well-characterized REPLAN. Mechanism C's EMISSION is proven correct — it drives markov `CASE_B` (rel 13.3) → `CASE_A` (rel 2.8e-16) and the cold MCP solves to the reference match (`pvcost = 2401.577`, complementarity 3.7e-09) — so the +1 payoff is fully de-risked. BUT the signature gate is NOT leak-free: a full-corpus golden-staleness run shows it also fires on cesam / ferts / sroute (not in the 6-model cohort), flattening their correct model-specific emit (dropping `$(darc(ip,ipp))`, `$(nonzero(ii,jj))`, `$(not sameas)` guards) — a regression. The leak's root is that markov's `σ=sp` coupling is a DERIVATIVE-structure property (a parameter coupling the constraint index to the variable's independent index), not the domain-aliasing property my gate tested. Per the design's REPLAN exit, Part-2 banks to a dedicated effort with a now-maximally-sharp spec: the emission is done+verified; the sole remaining blocker is the signature discriminator (distinguish param-coupled `σ=sp` from conditional-aliased structures).** Verifies Unknowns 1.2, 1.3 (the leak-freedom axis of 1.3 is REFUTED for the domain-only gate).

Reference: `MARKOV_OFFDIAGONAL_DESIGN.md` (Task 3) §3–§4 (Mechanism C), §6 (leak gate), §7 (REPLAN exit); `DAY1_MARKOV_CONTROL.md` (the `CASE_A` target + cold-match 2401.577); `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` §6 ("substantial rewrite").

---

## 1. Method

Prototyped Mechanism C in `src/kkt/stationarity.py` `_add_indexed_jacobian_terms` (editable install), ran the control gates, **reverted**. The prototype: a signature detector + a gated emission that, when it fires, emits the two clean reconciliation-(a) terms (Kronecker `nu_constr(var[0],var[1])` + off-diagonal `- sum(τ, deriv[σ=sp]·nu_constr(var[indep], τ))`, re-symbolizing a `σ=sp` representative via `_substitute_elements`) and **skips the buggy offset-group loop** for that (eq,var) pair — leaving the shared `_compute_index_offset_key` matcher untouched (per the design).

## 2. Emission — PROVEN correct (the +1 payoff is de-risked)

The prototype emits exactly the Day-1 `CASE_A` target on markov:
```
stat_z(s,i,sp)..  c(s,sp,i) + nu_constr(s,i)$(…)
                + sum(j, ((-1)*(b*pi(s,i,sp,j,sp))) * nu_constr(sp,j))$(…)
                + <lam_equil term>  - piL_z(s,i,sp)  =E= 0;   [0 spurious s__kkt groups]
```

| gate | result |
|---|---|
| KKT-residual (`kkt_residual.py data/gamslib/raw/markov.gms`) | **`CASE_A` — healthy**, `max` `stat_z` residual rel **2.8e-16** (was `CASE_B` 13.3) |
| cold-solve (no warm-start) | MODEL STATUS 1 Optimal, complementarity **3.7e-09**, `pvcost` = **2401.577** = reference (match) |

⇒ Mechanism C's emission logic reaches `CASE_A` + a genuine cold match. **The methodology→genuine +1 (floor 75→76) is achievable** — the emission is no longer the unknown.

## 3. Leak-freedom — REFUTED for the domain-only gate (the REPLAN trigger)

The design's 6-model cohort (`cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon`) stayed byte-identical — **but that cohort was not the complete risk set.** A **full-corpus** golden-staleness run (163 goldens) shows the gate ALSO fires on three non-cohort models:

| model | drift | DB status | what the gate wrongly did |
|---|---|---|---|
| **markov** | −11619 B | `model_optimal_presolve` (methodology) | intended (CASE_A) |
| **sroute** | −44 B | `path_solve_license` | `stat_x` `(1$(darc(ip,ipp))*lam_nb(i,ip))$(not sameas(i,ipp))` → bare `lam_nb(i,ip)` (dropped both guards) |
| **cesam** | −70 B (cold+presolve) | `model_infeasible` | `stat_a`/`stat_tsam` rewritten; dropped `$(nonzero(ii,jj))` guard |
| **ferts** | −28 B | `path_solve_license` | (same class — aliased-index flattening) |

The firings (instrumented): markov `eq=constr var=z mult=('sp','j') var=('s','i','sp')` (intended); sroute `eq=nb var=x mult=('i','ip') var=('i','ip','ipp')` (`ip` exact-matches var pos 1, canon-matches pos 0 — a false positive). None of cesam/ferts/sroute currently *matches*, so no live-match regression — but each carries a **structurally wrong emit** (dropped conditional guards), which the byte-identical discipline correctly flags as a leak.

**Root cause:** the domain-only signature ("a mult index exact-name-matches a later var position while canon-matching an earlier one") is satisfied by **any** model with an aliased index repeated in a later variable position (markov `z(s,i,sp)`, sroute `x(i,ip,ipp)`, cesam's SAM structures). markov's genuine `σ=sp` coupling is a **derivative-structure** property — the off-diagonal derivative is `-b·pi(s,i,σ,τ,sp)`, a *parameter* that couples the constraint index `σ` to the variable's independent index `sp` and is nonzero only on the `σ=sp` slice — whereas sroute's is a conditional constant `1$(darc(ip,ipp))` and cesam's is a log-term. A domain-only gate cannot tell them apart.

## 4. REPLAN + the sharpened bank

**REPLAN (the design's Day-2 exit): bank Part-2 to a dedicated effort.** But this bank is far sharper than DAY11's:
- **The emission is DONE and VERIFIED** (§2) — reconciliation (a), the re-symbolized off-diagonal, the offset-group suppression all reach `CASE_A` + cold-match. The dedicated effort inherits working emission code (in this control's history), not a "substantial rewrite" from scratch.
- **The SOLE remaining blocker is the signature discriminator** — it must fire on the genuine `σ=sp` param-coupling and NOT on conditional-aliased structures. The precise requirement: inspect the off-diagonal **derivative** (not just the domains) — fire only when the off-diagonal coefficient is a parameter whose argument at the constraint-index position is the variable's independent index (the `pi(...,σ→sp,...,sp)` shape), excluding conditional-constant (`1$(...)`) and non-coupled derivatives. This is the derivative-structure analysis DAY11 called the substantial part.
- **Leak-verification must be FULL-CORPUS, not the 6-model cohort** — the cohort missed cesam/ferts/sroute. The dedicated effort's leak gate is the full `check_golden_staleness.py` (163 goldens; ~the run this control used).

## 5. Day-3 implication

The design's REPLAN branch is "land Part-1 correctness-only (Day 3) + bank Part-2." **Reassess on Day 3:** Part-1 alone (the diagonal-Kronecker split) still touches the same shared emission and gives **0 bucket** (markov stays methodology at rel 1.55, `CASE_B`), and it risks the same false-positive class. Given the leak this control exposed, Day 3 should weigh Part-1-correctness-only (churns markov's golden for 0 bucket, must pass the full-corpus leak gate) against **banking the whole lever** (the cleaner "zero broken code" outcome) — likely the latter, carrying the proven emission + the discriminator spec to the dedicated Part-2 effort. Either way, **the markov +1 does not land in-sprint via the domain-only gate; the floor stays 75 pending the discriminator.**

## 6. Go / No-Go

**REPLAN — Part-2 banked, emission proven.** The control did exactly its job: it de-risked the payoff (CASE_A + cold-match achievable) AND surfaced the leak-freedom blocker **on Day 2** (earlier than the Day-5 checkpoint the front-loading targeted), with the remaining work reduced to a single precisely-specified discriminator. Zero broken code (`src/` byte-identical to `main`; markov re-emits to its committed golden). The `x.up=inf` / Case-c BANs held; `modelstat` asserted throughout.

---

**Document Status:** ✅ Complete — Sprint 36 Day 2 (markov Part-2 Mechanism-C control; emission PROVEN, gate leaks → REPLAN with sharpened bank)
**Last Updated:** 2026-08-07 · **Owner:** Sprint 36 Execution Team
