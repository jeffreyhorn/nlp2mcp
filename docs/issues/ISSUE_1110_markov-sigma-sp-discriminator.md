# ISSUE #1110 (Part 2) — markov `σ=sp` off-diagonal: derivative-structure discriminator

**Status:** 🔵 DESIGN COMPLETE — Phase-0 gate defined, not yet implemented
**Sprint:** 37 (P1, the +1-floor lever) · **Prep:** Task 4
**Files:** `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms`, the `offset_groups` region `:6136+`)
**Design:** `docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md`

## Problem

markov's `stat_z` emits 44 spurious offset groups instead of the single correct
off-diagonal term, making a `verified_convex` model a **methodology** match
(`model_optimal_presolve`) rather than a genuine one. The correct emission is
already PROVEN (Sprint 36 Day 2: `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16; cold
MCP solves to the reference **2401.577** + match ⇒ genuine floor **75 → 76**).

The sole blocker is the **gate**. Sprint 36's domain-only signature also fired on
`sroute`, `cesam` and `ferts`, flattening their correct model-specific emit
(dropping `$(darc(...))` / `$(nonzero(...))` guards) — a full-corpus leak the
6-model cohort missed.

## Fix (design)

Conjoin the existing domain-collision signature with a **derivative-structure**
test: fire only when the off-diagonal coefficient's **value branch** contains a
`ParamRef` that couples an equation-domain index to the variable's
collision-position index (markov's `pi(s,i,σ,τ,sp)`). The two leak classes are
excluded structurally — `sroute`'s param appears **only inside a `$`-condition**
(value is `Const(1.0)`), and `cesam`'s derivative is **variable-bilinear**
(`VarRef x + VarRef err1`, no `ParamRef` at all).

## Phase 0: Acceptance Gate

### Correctness

`python scripts/diagnostics/kkt_residual.py data/gamslib/raw/markov.gms` must
report **`CASE_A`** (max `stat_z` residual rel < 1e-3; expected ≈ 2.8e-16, from
the proven Day-2 emission), with dual transfer **CONSISTENT**. Before the fix it
reports `CASE_B`, `stat_z(empty,disrupted,empty)` rel **1.33e+01**.

### Bucket / KPI

The **cold** (no-presolve) markov MCP must solve `MODEL STATUS 1 Optimal` with
`pvcost = 2401.577` (the NLP reference) and register a **match**, moving markov
from the 30-model presolve-match (methodology) partition into the genuine floor:
**genuine floor 75 → 76**. `modelstat` asserted, not inferred.

### Leak-freedom (full corpus — MANDATORY)

`make leak-check MODEL=markov` must print **`LEAK GATE PASS`** (the unqualified
full-corpus form — *not* `PARTIAL`, which would mean the sweep was narrowed).
This asserts that of all 163 in-scope goldens **only** `markov_mcp.gms` drifts;
`cesam`, `ferts`, `sroute` (the Sprint-36 leaks) and the 2-D cohort must be
byte-identical. A `PARTIAL` verdict, any `LEAK:` line, or a `NO-OP:` line fails
the gate. Do **not** run `make regen-goldens` to clear drift — that launders a
leak into the goldens.

### Regression guard

`tests/.../test_shape_markov_diagonal_kronecker` (the fast in-process fixture)
must **fail before** the fix and **pass after**, asserting the emitted `stat_z`
contains the single `sum(j, …pi(s,i,sp,j,sp)…*nu_constr(sp,j))` off-diagonal and
**zero** `s__kkt*` spurious offset groups. It must `pytest.skip` when
`data/gamslib/raw/markov.gms` is absent (CI lacks the raw corpus). Full quality
gate (`make typecheck && make format && make lint && make test`) green.

## REPLAN exit

If the conjoined predicate cannot be made leak-free full-corpus, fall back to a
narrower per-signature allowlist (fire only on the exact
`(mult_domain, var_domain, param-name-coupling)` shape observed on markov), and
if that also leaks, bank Part-2 again with the new evidence. Part-1
(Kronecker-only diagonal) alone is **0 bucket** and still needs the same gate, so
it is not a consolation landing.

## References

- `docs/planning/EPIC_4/SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md` — emission proven; domain-only gate leaks
- `docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md` — Mechanism C + the target form
- `docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md` — the `make leak-check` gate
- `docs/planning/EPIC_4/SPRINT_37/BASELINE_RECONFIRMATION.md` §3.1 — the fingerprint re-confirmed on current `main`
