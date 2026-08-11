# ISSUE #1110 (Part 2) — markov `σ=sp` off-diagonal: derivative-structure discriminator

**Status:** ✅ **LANDED** (Sprint 37 Day 2, `3190c74f`) — all four Phase-0 criteria measured on the landed tree; the `shape_markov_diagonal_kronecker` regression fixture follows on Day 3
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

> Restructured in Sprint-37 Prep Task 10 to carry the four `### ` subsections
> CONTRIBUTING.md §392–447 requires (the prior criteria-only decomposition failed
> the drafted Phase-0 CI check — see `SPRINT_37/P7_INFRA_CATALOG.md` §2.4). The
> four acceptance criteria are retained verbatim below as additional subsections.

### Hand-Derived KKT Shape

Constraint (`markov.gms`), with `Alias (s,sp,spp), (i,j)`:

```
constr(sp,j).. sum(spp, z(sp,j,spp)) - b*sum((s,i,spp), pi(s,i,sp,j,spp)*z(s,i,spp)) =e= beta;
```

Lagrangian (the `equil`/`cost` rows are unaffected and omitted):

```
L = sum((s,i,spp), c(s,spp,i)*z(s,i,spp))
  + sum((sp,j), nu_constr(sp,j) * [ sum(spp, z(sp,j,spp))
                                    - b*sum((s,i,spp), pi(s,i,sp,j,spp)*z(s,i,spp)) - beta ])
```

∂L/∂z(s,i,sp) has exactly three parts:

1. **objective** → `c(s,sp,i)`.
2. **the direct reference** `sum(spp, z(sp,j,spp))` contributes `nu_constr(sp,j)` at
   `(sp,j) = (s,i)` — a **Kronecker diagonal**, i.e. a *bare* `+ nu_constr(s,i)`
   term with **no** enclosing `sum`.
3. **the coupling term** contributes `- b*sum((sp,j), pi(s,i,sp,j,sp)*nu_constr(sp,j))`.
   Because `pi` is assigned **only** on the `σ=sp` slice (`pi(s,i,sp,j,sp) = pr(i,j)`),
   every `sp ≠ sp_var` entry is structurally zero and the double sum collapses to a
   **single** sum over `j` at `sp = ` the variable's own third index.

**Stationarity (target):**

```
stat_z(s,i,sp)..  c(s,sp,i) + nu_constr(s,i)
                  - b*sum(j, pi(s,i,sp,j,sp)*nu_constr(sp,j))
                  - piL_z(s,i,sp)  =e= 0
```

The defect is that (2) and (3) are **fused**: the emitter folds the Kronecker `1`
into the off-diagonal coefficient (`(1 - b*pi(...)) * nu_constr(s,i)`) and then
wraps that product in a `sum` over alias indices it does not depend on, while
enumerating the `sp ≠ sp_var` slices it should have recognised as zero.

### Expected Emit Pattern

`markov_mcp.gms` after the fix — one `nu_constr` diagonal term, one off-diagonal
sum, and **zero** `s__kkt*` groups:

```
stat_z(s,i,sp).. c(s,sp,i) + nu_constr(s,i)
               + sum(j, ((-1) * (b * pi(s,i,sp,j,sp))) * nu_constr(sp,j))
               - piL_z(s,i,sp) =E= 0;
```

Today's emit instead carries **45** distinct `s__kkt<N>` sums (44 spurious
off-diagonal groups plus the fused diagonal), each guarded by an enumerated
`ord(s__kktN) = k` / `sameas(s, '<member>')` disjunction — the enumeration
blow-up that is the visible symptom of the collapse.

**This is the prep-doc hypothesis** (PR24): the `file:line` surface is the one
traced below, not this pattern.

### Verification Methodology

1. **Emit-bug vs non-convexity discriminator** (the CONTRIBUTING-mandated
   Case-a/b/c harness):
   ```bash
   .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/markov.gms
   ```
   Baseline is `CASE_B`, `stat_z(empty,disrupted,empty)` rel **1.33e+01**; the fix
   must produce **`CASE_A`** (rel ≈ 2.8e-16) with dual transfer **CONSISTENT**.
2. **Pattern match on the regenerated emit:**
   ```bash
   grep -c 's__kkt' data/gamslib/mcp/markov_mcp.gms      # must be 0 (baseline: 45 groups)
   grep -o '+ nu_constr(s,i)' data/gamslib/mcp/markov_mcp.gms   # bare diagonal present
   ```
3. **Full-corpus byte-diff:** `make leak-check MODEL=markov` (see *Leak-freedom*).
4. **Cold solve:** `modelstat` read from the listing, never inferred (see *Bucket / KPI*).

### PROCEED/REPLAN Signal

**PROCEED** iff all four acceptance criteria below hold, with *Leak-freedom* the
binding one — Sprint 36 proved the emission and was blocked solely on the gate.

**Traced Fix-Surface (Day-0):** `src/kkt/stationarity.py`,
`_add_indexed_jacobian_terms` — **detect** at the `offset_groups` construction
(`:6136–6158`, before the `#1038` consolidation at `:6171`), **suppress** the
spurious groups in that same dict, **emit** the collapsed off-diagonal in the
correction-append region (`:7214+`). Line numbers re-verified against current
`main` in Prep Task 10 (`:6136` = the `offset_groups` dict init; `:6171` = the
`len(offset_groups) > 1` branch). Evidence: Sprint-36 Day-2 implemented the
emission **in `src/`** at this surface and measured `CASE_A` + the cold match
(`DAY2_MARKOV_OFFDIAG_CONTROL.md`); Prep Task 4 extracted the three competing
derivative ASTs live from `compute_constraint_jacobian` → `get_derivative` and
scanned the conjoined predicate across 142 models, firing on exactly `['markov']`.
**`_compute_index_offset_key` (`:4969`) is NOT touched** — that shared matcher is
the cohort-leak surface, and leaving it alone is Mechanism C's premise.

**REPLAN** on any of: the predicate leaks full-corpus; the emitted `stat_z` does
not reach `CASE_A`; the cold solve does not reach `MODEL STATUS 1`. See
*REPLAN exit* below.

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

`tests/unit/kkt/test_shape_markov_diagonal_kronecker.py` must **fail before** the
fix and **pass after**: the diagonal multiplier `nu_constr(s,i)` must move from
*inside* a `sum((s__kktN,j), …)` (where it is multiplied by `card(s)·card(j)`) to
a **bare additive term**, with the off-diagonal emitted as a single sum whose
coefficient no longer carries the Kronecker `1 -`.

**Corpus-free, not skip-if-absent** (corrected in Prep Task 10): the fixture
builds an inline synthetic via `parse_model_text` → `assemble_kkt_system` →
`build_stationarity_equations` — **measured at 0.61 s**, reproducing the
`CASE_B` shape at `|s|`=3. A `pytest.skip` guard on `data/gamslib/raw/markov.gms`
would make the fixture **inert in CI**: `ci.yml` provisions only the 5 `--fast`
models and markov is not among them. It must **not** assert the `s__kkt*` group
count (15 synthetic vs 45 real) — only the structural diagonal/off-diagonal
split. Full quality gate (`make typecheck && make format && make lint && make
test`) green. See `SPRINT_37/P7_INFRA_CATALOG.md` §1.1.

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
