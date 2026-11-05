# ISSUE #1789 — stationarity: a scalar variable's row over a head-offset equation drops or collapses its lead/lag references (`stat_step`: lnts, robot)

**GitHub:** [#1789](https://github.com/jeffreyhorn/nlp2mcp/issues/1789) · **Status:** 🟡 **OPEN** — filed Sprint 40 Day 8 (2026-10-31); P5 (Days 8–10)
**Layer:** **KKT / stationarity**, the scalar-variable Jacobian-transpose path `_add_jacobian_transpose_terms_scalar` (`src/kkt/stationarity.py`)

## Summary

A **scalar** variable that multiplies lead/lag references inside an **indexed, head-offset** equation gets a wrong stationarity row. The confirmed corpus cases are `lnts` and `robot`, both through `step` in `stat_step` (KKT residual `case_b`, worst row `stat_step`). The candidates `glider` and `rocket` are not yet confirmed.

## Mechanism (traced, Sprint 40 Day 8)

**Layer:** `src/kkt/stationarity.py::_add_jacobian_transpose_terms_scalar`. A scalar variable's term for an indexed constraint is built from `entries[0]`'s derivative alone, and its labels are mapped to symbols by set membership only (`_build_constraint_element_mapping`). The indexed path has an offset substitution (#1162, `_apply_offset_substitution`); this path has none. Two symptoms follow from the one cause:

- **Lead head** (`lnts`: `pos_eqn(c+2,h+1).. … + 0.5*step*(y(c+2,h) + y(c+2,h+1))`): the representative's derivative holds `u(h1) + u(h2)`, both labels of `h`, and both map to `h`, giving `2*u(h)`.
- **Lag head** (`robot`: `rho_eqn(h-1).. … + 0.5*step*(rho_dot(h) + rho_dot(h-1))`): `entries[0]` is the **boundary** instance, whose derivative has only `u(h1)` (`u(h0)` does not exist). That single term is generalised to every instance, so `rho_dot(h-1)` is dropped.

## Minimal reproducers

```gams
Set h / h1*h5 /;
Parameter tgt(h);  tgt(h) = power(ord(h),3);
Variable x(h), u(h), obj;  Positive Variable step;
Equation dyn(h), defobj;
dyn(h+1).. x(h+1) =e= x(h) + 0.5*step*(u(h) + u(h+1));        * lead: 2*u(h)
* dyn(h-1).. x(h) =e= x(h-1) + 0.5*step*(u(h) + u(h-1));      * lag: u(h) only
defobj.. obj =e= sum(h, sqr(x(h) - tgt(h))) + sum(h, sqr(u(h) - ord(h))) + sqr(step - 1);
x.fx('h1') = 0;
Model m / all /;  solve m using nlp minimizing obj;
```

| form | emitted `stat_step` term | MCP | NLP |
|---|---|---|---|
| lead | `sum(h, -(2*u(h)*0.5) * nu_dyn(h))` | 68.577 | 68.5456 |
| lag | `sum(h, -(u(h)*0.5) * nu_dyn(h))` | 72.689 | 68.5456 |

The correct term is `sum(h, -0.5*(u(h) + u(h±1)) * nu_dyn(h))`, with the offset reference present wherever the head allows it.

## Corpus evidence (licensed, Sprint 40 Day 8, `kkt_residual.py`)

| model | verdict | worst row | next rows |
|---|---|---|---|
| lnts | `CASE_B` | `stat_step` rel **9.66** | `stat_y(y4,h1)` 0.008 |
| robot | `CASE_B` | `stat_step` rel **10.1** | `stat_the(h0)` 0.21, `stat_rho(h0)` 0.18, `stat_rho(h50)` 0.17: a smaller boundary group, not yet attributed |

**Candidates, unconfirmed:** `glider` (`case_b`, but `stat_step` is second to `stat_cl`) and `rocket` (`CASE_C_OBJDEF`, `stat_step` second). Each needs a fresh diagnosis before it is counted.

## Relations

- `lnts` (`ISSUE_1694`, verdict C): its banked diff is NOT re-applied. This class is the second defect Prep Task 8 found under it.
- `ISSUE_1462` (rocket) should cross-reference this issue.
- Sprint 40 P5 (Days 8–10). **No Solve is projected** (lnts verdict C).

## Phase 0: Acceptance Gate (Sprint 40 Day 8, P5)

### Layer

**KKT / stationarity**: `_add_jacobian_transpose_terms_scalar`. It builds a scalar variable's term for an indexed constraint from `entries[0]`'s derivative alone, mapped by set membership only.
- **Traced on Day 8 by instrumenting the representative** (minimal fixtures above): the lead form's `entries[0]` derivative is `-0.5*(u(h1) + u(h2))`; the lag form's is `-0.5*u(h1)`, the boundary instance.
- The AD derivative is correct per instance. The loss happens when ONE instance is generalised by membership.

### Nearest Existing Mechanism

**Nearest:** the indexed path's offset handling in `_add_indexed_jacobian_terms`. It groups entries by offset (`_compute_index_offset_key`, #1045), picks representatives that avoid boundaries, and converts offset labels to `IndexOffset` (`_apply_offset_substitution`, #1162).

**Why it does not apply:** the scalar path has none of it. It is one branch, with no offset grouping and no substitution: #730 added it for scalar variables over indexed constraints and only lifted labels to set names.

### Positive Control

A scalar variable whose derivative over an indexed constraint references only the constraint's OWN index already emits correctly. For example, `e(h).. x(h) =e= step*u(h)` gives `sum(h, -u(h)*nu_e(h))`. It must stay byte-identical, and so must every scalar-variable row in the corpus that holds no offset reference.

### Hand-Derived KKT Shape

- `dyn(h+1).. x(h+1) =e= x(h) + 0.5*step*(u(h) + u(h+1))`, multiplier `nu_dyn(h)` paired with the control index: `∂dyn(h)/∂step = -0.5*(u(h) + u(h+1))`.
- **Stationarity:** `stat_step.. ∂f/∂step + sum(h$(ord(h) < card(h)), -0.5*(u(h) + u(h+1)) * nu_dyn(h)) =E= 0`.
- **The lag form** `dyn(h-1)..` gives `-0.5*(u(h) + u(h-1))` over the instances the head allows.

### Expected Emit Pattern

The scalar path re-symbolises each offset reference as an `IndexOffset` relative to the constraint's control index (`u(h+1)`, `u(h-1)`), from a representative that is not a boundary instance. It is the analogue of #1162 for the indexed path. Membership-only mapping stays for references without an offset.

### Verification Methodology

1. **Fail-before / pass-after** on both minimal forms: the row, and the solve against the NLP (68.5456; before: 68.577 lead, 72.689 lag).
2. The positive control (own-index-only scalar rows) byte-identical.
3. `kkt_residual.py` on **lnts** and **robot**: `stat_step` within the harness tolerance (0.001). A change of worst-row label alone does not pass.
4. The full leak gate, with every drifted golden re-solved by `--resolve-changed`; then `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–4 hold and the resolver holds every bucket.
- **REPLAN** on any backward move, or if lnts / robot `stat_step` stays out of tolerance (then a second defect sits in the same row).
- **No Solve is projected** (lnts verdict C). robot's smaller boundary rows (`stat_the(h0)` 0.21, `stat_rho(h0)` 0.18) are **not** claimed by this item. If they persist after the fix they are a separate defect, banked and routed.
- **The shared-mechanism question (PLAN §3 P5) is answered: one mechanism, two symptoms.** lnts and robot are not split.

## Day 9 (P5, 2 h): a prototype, and a second mechanism in the same row

**Prototype, not landed.** It lives in a scratch worktree, behind an environment flag. Day 9's PR is P6, which is gated on byte-identical goldens, so a `stat_step` change cannot ride along. Two changes in `_add_jacobian_transpose_terms_scalar`:

1. **The representative** is the instance with the most distinct leaf references, ties going to the first. A lag head's boundary instance, which lost a reference, is therefore not the one generalised. GAMS evaluates the out-of-range `u(h-1)` at the boundary as 0, so the generalised term is exact there too.
2. **`_apply_offset_substitution`** is keyed on the **constraint's** labels, `(eq_indices, eq_indices, mult_domain)`, rather than the variable's (a scalar has none). It runs before `_replace_indices_in_expr` and is skipped for a circular-offset equation, the indexed path's guard.

| fixture | NLP | main | prototype | prototype `stat_step` term |
|---|---|---|---|---|
| lead | 68.5456 | 68.577 | **68.546** | `sum(h, -((u(h) + u(h+1))*0.5) * nu_dyn(h))` |
| lag | 68.5456 | 72.689 | **68.546** | `sum(h, -((u(h) + u(h-1))*0.5) * nu_dyn(h))` |
| own-index control | | | `stat_step` byte-identical | `sum(h$(ord(h) > 1), -u(h) * nu_dyn(h))` |

**Still owed (Day 10):** the leak gate and the resolver over the corpus, then `kkt_residual.py` on lnts and robot (Verification steps 3–4).

**A second mechanism in the same function: a quoted literal is lifted to the set.**
- **Shape:** `dyn(h)$(ord(h)>1).. x(h) =e= x(h-1) + step*(u(h) + u('h3'))`.
- **Emitted:** `sum(h$(ord(h) > 1), -(2*u(h)) * nu_dyn(h))`.
- **Cause:** AD keeps the literal quoted (`u("h3")`), and `_replace_indices_in_expr` with the constraint element map lifts it to `u(h)`. Called directly, `u(h2) + u("h3")` gives `u(h) + u(h)`.
- **Relation to the prototype:** it neither causes nor fixes this. The fix is a separate one, preserving quoted literals in the scalar path's re-symbolisation.
- **Gate:** add the literal fixture as a third form.

**Found while building the control, unrelated to `stat_step`: #1793.** The own-index fixture's `stat_x` emits `$(ord(h+1) > 1)`, which is illegal GAMS. dinam's golden carries the same construct.

## Day 10 (P5): banked — the REPLAN signal fired

The Day-9 prototype, made production-shaped, went through the full gate. **The implementation is archived as the durable commit [`f57bc1d7`](https://github.com/jeffreyhorn/nlp2mcp/commit/f57bc1d7eee0ba0af7aee42e8ac9271e4c103e91) on branch `banked/1789-scalar-offset` (fix + its 4 unit tests, against `1abcd687`; not for merge).** The `stationarity.py` diff is also on [#1789](https://github.com/jeffreyhorn/nlp2mcp/issues/1789#issuecomment-6643421979), in a collapsed block.
- **Gate:** `make test` 5,772 passed. The leak gate was complete, with 0 timeouts.
- **Drift:** 7 goldens over exactly the predicted 4 models.

| model | resolver | `stat_step` |
|---|---|---|
| lnts | `model_infeasible` = same | the intended terms appear, but **`kkt_residual.py` rel 9.66 → 13.26** (`case_b`) |
| robot | ⛔ **BACKWARD** → `path_solve_terminated` | the intended terms (`rho_dot(h) + rho_dot(h-1)`, …) |
| rocket | ⛔ **BACKWARD** → `path_solve_terminated` | the intended terms (`v(h) + v(h-1)`, …) |
| glider | mismatch = same | **wrong**: `sum(h, … (vel(c,i) + vel(c,h)) …)` |

**Three requirements the Day-9 fixtures did not cover:**
1. **The offset term needs a boundary guard.** Day 9 said GAMS's out-of-range-is-0 rule makes the generalised term exact at the boundary. That is **false under a nonlinear operation**.
   - robot's `u_the(h-1) / i_the(h-1)` at the first `h` divides by the out-of-range `i_the(h0)`, and `stat_step` evaluates to UNDF (`kkt_residual.py`: `division by zero`, EXECERROR).
   - rocket's `… / m(h-1)` is the same shape.
2. **A subset equation domain.** glider's constraint runs over `i(h)`. The offset label resolves through the parent `h`, which leaves an uncontrolled `h`, and #949's wrap then adds a blanket `sum(h, …)`.
3. **A second defect in lnts' row, not yet attributed.** The residual gets worse even with the intended terms present. The candidate is the 2-D head `pos_eqn(c+2,h+1)`, whose `c+2` is substituted too.

**Gate additions for the next attempt:**
- a division-under-lag fixture, which must solve;
- a subset-domain fixture;
- lnts `stat_step` within tolerance, which a label change alone does not satisfy.
