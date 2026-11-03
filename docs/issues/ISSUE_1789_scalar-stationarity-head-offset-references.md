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
