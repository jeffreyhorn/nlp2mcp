# Sprint 36 — Day 3: markov P1 disposition — BANK the lever (Part-2 discriminator = dedicated effort) + budget reallocation

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day3-markov-bank` · **Scope:** docs-only (the REPLAN disposition from Day 2); no `src/`, no golden change.

**Outcome: BANK the markov lever. Day 2 proved Mechanism C's emission reaches `CASE_A` + cold-match (the +1 is de-risked) but the domain-only signature gate leaks onto three structurally-distinct models (cesam / ferts / sroute); a leak-free gate requires a derivative-structure discriminator that is genuinely the "substantial rewrite" (DAY11) — not responsibly landable in-day without regression risk. Neither branch of the design's Day-2 REPLAN exit ships `src/` this sprint: (a) landing Mechanism C now would regress cesam/ferts/sroute; (b) Part-1-correctness-only is 0 bucket, churns markov's golden, and carries the same false-positive class. So the whole lever banks to a dedicated Part-2 effort with the proven emission + the sharpened discriminator spec. The freed Days-3–5 markov budget reallocates to P3 fawley (Day 4) and P2 sarf (Days 6–7). Genuine floor stays 75 (markov +1 does NOT land in-sprint).**

Reference: `DAY2_MARKOV_OFFDIAG_CONTROL.md` (the control: emission proven, gate leaks), `DAY1_MARKOV_CONTROL.md` (the `CASE_A` cold-match target 2401.577), `MARKOV_OFFDIAGONAL_DESIGN.md` §7 (REPLAN exit), `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` §6.

---

## 1. The decision

**BANK the markov P1 lever (Part-1 + Part-2). No `src/` ships this sprint.**

The design's Day-2 REPLAN exit offered "land Part-1 correctness-only + bank Part-2." Day 2's full-corpus leak evidence makes **banking the whole lever** the correct branch:

| option | verdict |
|---|---|
| **Land Mechanism C now** (domain-only gate) | ❌ regresses cesam/ferts/sroute (drops `$(darc(ip,ipp))`, `$(nonzero(ii,jj))`, `$(not sameas)` guards) — a shipped correctness regression |
| **Land Part-1-correctness-only** (diagonal split alone) | ❌ 0 bucket (markov stays methodology at `CASE_B` rel 1.55); churns markov's golden; touches the same shared emission with the same false-positive class; no full-corpus leak guarantee |
| **Bank the whole lever** (proven emission + discriminator spec → dedicated effort) | ✅ zero broken code; the +1 is de-risked and precisely scoped for the dedicated effort |

## 2. Why the discriminator is a dedicated effort (not an in-day change)

Mechanism C fires when a mult-domain index exact-name-matches a *later* var position while canon-matching an *earlier* one — a **domain** property satisfied by any aliased-index-in-a-later-position model. markov's genuine `σ=sp` coupling is a **derivative-structure** property, and the three leaked models each have a *structurally distinct* off-diagonal derivative:

- **markov (must fire):** `-b·pi(s,i,σ,τ,sp)` — a **parameter product** coupling the constraint index `σ` to the variable's independent index `sp` (nonzero only on `σ=sp`).
- **sroute (must NOT fire):** `(1$(darc(ip,ipp)))` — a **`Const(1)` gated by a set-membership `$`**, no param coupling.
- **cesam (must NOT fire):** a **variable-bilinear** term (`x(jj) + err1(…)`), no param coupling.

A leak-free discriminator must fire on the first and exclude the latter two **and every future aliased-index model**, verified across the **full corpus** (163 goldens — the 6-model cohort missed all three leaks). Distinguishing "param-coupled `σ=sp`" from "conditional-constant" from "variable-bilinear" robustly, under alias ambiguity, is exactly the offset/multi-pattern-machinery rewrite DAY11 flagged. Shipping a heuristic that happens to pass on markov but is fragile against the corpus violates the project's control-first, zero-broken-code discipline (the S30–S35 pattern: every deep track banked/REPLAN'd rather than ship risky `src/`).

## 3. Carryforward spec (maximally sharp — for the dedicated Part-2 effort)

The dedicated effort inherits a **proven emission** and a **single precisely-specified blocker**:

1. **Emission (DONE + VERIFIED, Day 2):** reconciliation (a) — Kronecker diagonal `nu_eq(var[0],var[1])` + off-diagonal `- sum(τ, deriv[σ=sp]·nu_eq(var[indep], τ))` (re-symbolize a `σ=sp` representative via `_substitute_elements`) + suppress the offset-group loop for the firing (eq,var) pair. Reaches markov `CASE_A` (rel 2.8e-16) + cold-match `pvcost = 2401.577`. Leaves the shared `_compute_index_offset_key` matcher untouched.
2. **Blocker (the SOLE remaining piece):** the signature **discriminator** — extend the domain gate with a derivative-structure test that fires only on the genuine param-coupled `σ=sp` (a `ParamRef` coupling the constraint index and the variable's independent index), excluding conditional-constant and variable-bilinear derivatives.
3. **Leak gate:** **full-corpus** `check_golden_staleness.py` (163 goldens) must show **only markov drifts** — NOT the 6-model cohort (which missed cesam/ferts/sroute).
4. **Acceptance:** markov `CASE_A` + cold `model_optimal` + match (`modelstat` asserted) → genuine floor 75 → 76; the fast `shape_markov_diagonal_kronecker` fixture (`FIXTURE_AND_HARNESS_CATALOG.md` §1) + the sharpened `test_markov_stationarity_has_correction_term` land *with* the fix (they stay red/`slow` until then — not added now, as they would be red against the unfixed emit).

## 4. Budget reallocation

The schedule (`PLAN.md`) front-loaded markov Days 1–3 specifically so a REPLAN would surface early and free budget. It surfaced on **Day 2**. Reallocation:
- **Days 3–5 markov budget → P3 fawley (Day 4) + P2 sarf (Days 6–7)** get more room (both emit-track candidates).
- **Checkpoint 1 (Day 5)** records: markov banked (floor flat 75); no `src/` shipped Days 1–3; determinism/`--resolve-changed` unaffected (no golden churn).
- The dedicated markov Part-2 effort → **Sprint 37 carryforward** (or a dedicated markov-discriminator effort), with §3 as its implementer-ready spec.

## 5. KPI impact

**Genuine floor stays 75** — the markov +1 does not land in-sprint (the domain-only gate can't ship; the discriminator is a dedicated effort). This is within the honest projection (`PLAN.md` §2: "floor 75 or 76, markov-contingent" → the **75 branch**). DB byte-unchanged; `src/kkt/stationarity.py` byte-identical to `main`; markov re-emits to its committed golden (`CASE_B`, unchanged).

## 6. Go / No-Go

**Bank — clean.** Zero broken code (`src/` byte-identical to the anchor; no golden churn). The control-first discipline held: the payoff was de-risked (emission proven) and the leak-freedom blocker surfaced + precisely scoped **before** any risky `src/` shipped. The sprint proceeds to P3 fawley (Day 4) with the freed budget; markov Part-2 carries to a dedicated effort with the sharpest possible hand-off. `modelstat`-assert / `x.up=inf`-BAN / Case-c-BAN disciplines all held.

---

**Document Status:** ✅ Complete — Sprint 36 Day 3 (markov P1 BANK disposition + budget reallocation; floor flat 75, emission-proven bank)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team
