# Accounting Variable Detection Design

**Task:** Sprint 20 Prep Task 7 — Design Accounting Variable Detection (#764 mexss)
**Branch:** `planning/sprint20-task7`
**Date:** 2026-02-19
**Status:** DESIGN COMPLETE

---

## 1. mexss Pattern Characterization

### Model Overview

`data/gamslib/raw/mexss.gms` is an LP (linear program) that decomposes its objective `phi` into
named cost components using auxiliary accounting equations. Five variables are purely definitional:

| Variable | Defining Equation | RHS Summary | Appears In |
|----------|-------------------|-------------|------------|
| `phi` | `obj` | `phipsi + philam + phipi - phieps` | `obj` only |
| `phipsi` | `apsi` | `sum((cr,i), pd(cr)*u(cr,i))` | `obj` only |
| `philam` | `alam` | `sum((cf,i,j), muf*x + muv*v + mue*e)` | `obj` only |
| `phipi` | `api` | `sum((cf,j), pv(cf)*v(cf,j))` | `obj` only |
| `phieps` | `aeps` | `sum((cf,i), pe(cf)*e(cf,i))` | `obj` only |

All five are declared as free scalars (`Variable phi, phipsi, philam, phipi, phieps`; no
`Positive Variable` or bounds). `phi` is the objective variable; `phipsi`, `philam`, `phipi`,
`phieps` are the accounting variables.

### Why mexss Fails as an MCP

The NLP→MCP transformer generates stationarity equations for all non-objective variables,
including the four accounting variables. After AD simplification, these reduce to:

```gams
stat_phieps.. -1 + nu_aeps =E= 0;   * forces nu_aeps = 1
stat_philam..  1 + nu_alam =E= 0;   * forces nu_alam = -1
stat_phipi..   1 + nu_api  =E= 0;   * forces nu_api  = -1
stat_phipsi..  1 + nu_apsi =E= 0;   * forces nu_apsi = -1
```

These force the multipliers to specific numeric values. The stationarity equations for the
actual optimization variables (`u`, `v`, `e`) reference these multipliers:

```gams
stat_u(c,i)$(cr(c)).. ((-1)*pd(c))*nu_apsi + ... =E= 0;
stat_e(c,i)$(cf(c)).. ((-1)*mue(i))*nu_alam + ((-1)*pe(c))*nu_aeps + ... =E= 0;
stat_v(c,j)$(cf(c)).. ((-1)*muv(j))*nu_alam + ((-1)*pv(c))*nu_api + ... =E= 0;
```

With `nu_apsi=-1`, `nu_alam=-1`, `nu_api=-1`, `nu_aeps=1` forced, the stationarity conditions
for the optimization variables become linear combinations of inequality multipliers
(`lam_mbf`, `lam_mbr`, etc.) that must simultaneously satisfy the complementarity conditions.
PATH reports locally infeasible (residual 3.46, model_status=5) after 8,629 iterations.

### Do the Accounting Variables Match All Three Proposed Criteria?

| Criterion | phipsi | philam | phipi | phieps |
|-----------|--------|--------|-------|--------|
| C1: LHS of exactly one =E= equation | ✓ | ✓ | ✓ | ✓ |
| C2: Does not appear in RHS of its own defining equation | ✓ | ✓ | ✓ | ✓ |
| C3: Only other appearance is in objective-defining equation (obj) | ✓ | ✓ | ✓ | ✓ |

All four pass all three criteria. `phi` (the objective variable) is already excluded from
stationarity by the existing `should_skip_objvar` logic.

---

## 2. Proposed Detection Algorithm

### Algorithm: Conservative Accounting Variable Detection

A variable `v` is considered a **candidate accounting variable** if it satisfies all of the
following criteria C1–C4. Final classification as an accounting variable (i.e., no stationarity
equation generated) additionally requires Criterion C5 (see below) to avoid false positives.

**Criterion C1 — Scalar VarRef LHS**
`v` appears as a pure `VarRef` on the left-hand side of exactly one `=E=` equation `E_def(v)`.
Indexed variables (where the LHS has an index domain) are excluded from consideration.

*IR-level check:* `edef.relation == Rel.EQ`, `isinstance(lhs, VarRef)`, `len(edef.domain) == 0`,
and `sum(1 for n,e in ir.equations.items() if e.relation==Rel.EQ and isinstance(e.lhs_rhs[0], VarRef) and e.lhs_rhs[0].name.lower() == v.lower()) == 1`

**Criterion C2 — Not Self-Referential**
`v` does not appear anywhere on the right-hand side (or condition) of `E_def(v)`.

*IR-level check:* `not contains_var(rhs, v)` where `contains_var` does an AST walk.

**Criterion C3 — Appears In (and Only In) Objective-Defining Equation**
The only equation (other than `E_def(v)`) where `v` appears must be the objective-defining
equation `E_obj` (the unique `=E=` equation with the objective variable on its LHS), and `v`
must appear at least once in `E_obj`. Variables that appear in no other equation (e.g.,
himmel11's `g2/g3/g4`) do **not** pass C3 — they are auxiliary/intermediate variables, not
objective-decomposition accounting variables, and excluding their stationarity equations would
produce an under-constrained MCP.

*IR-level check:* First verify `v` appears in `E_obj`:
`appears_in_obj = any(name.lower() == E_obj.lower() and (contains_var(lhs, v) or contains_var(rhs, v)) for name, edef in ir.equations.items() for lhs, rhs in [edef.lhs_rhs])`
and require `appears_in_obj is True`. Then, for all `(name, edef)` in `ir.equations` where
`name != E_def(v)`: if `contains_var(lhs, v) or contains_var(rhs, v)`, then
`name.lower() == E_obj.lower()`.

**Criterion C4 — Not Referenced in Any Inequality Constraint**
`v` does not appear in any `=G=` or `=L=` equation body.

*IR-level check:* For all `(name, edef)` where `edef.relation in (Rel.GE, Rel.LE)`:
`not (contains_var(edef.lhs_rhs[0], v) or contains_var(edef.lhs_rhs[1], v))`.

> **Note:** C4 is redundant with C3 for all known cases (if C3 passes, C4 trivially passes),
> but is included as an explicit guard for correctness.

### Additional Required Discriminator: OBJ-CHAIN-ONLY

The four criteria above are **necessary but not sufficient** to distinguish mexss from
currently-solving models with identical structural patterns. A 5th criterion is required:

**Criterion C5 — The Accounting Variable's Chain Terminates at the Objective Variable**
Every equation in the chain `E_def(v) → E_obj → objvar` must consist entirely of accounting
variables (C1–C4 candidates) or the objective variable itself. No path from `v` through
equality chains reaches an optimization variable (i.e., a variable with non-trivial stationarity).

*Rationale:* In demo1, `revenue/mcost/labcost/labearn` appear in `income` (the objective-defining
eq), and `income` is paired as `income.yfarm`. These accounting vars appear in the *same equation
as the objective variable* — the substitution is clean. In himmel11, `g2/g3/g4` have no equation
chains at all (they appear nowhere except their own defining equation). Neither pattern causes
infeasibility because the stationarity equations, while forcing specific multiplier values, are
consistent with the rest of the system. The mexss failure is caused by over-constraining the
multipliers for the *optimization variables* (`u`, `v`, `e`, `z`), not the accounting variables.

*Current assessment:* Static C5 check requires verifying consistency of the reduced system, which
is not feasible from static IR inspection alone.

---

## 3. Static Analysis Feasibility

| Criterion | Computable from Static IR? | IR Attributes Needed | Cost |
|-----------|---------------------------|----------------------|------|
| C1: Scalar VarRef LHS of exactly one =E= | ✓ Yes | `ir.equations`, `edef.relation`, `edef.domain`, `lhs_rhs[0]` type | O(E·V) |
| C2: Not on own RHS | ✓ Yes | `edef.lhs_rhs[1]`, AST walk | O(E · AST_size) |
| C3: Only in obj-defining eq | ✓ Yes | All `edef.lhs_rhs`, `ir.objective.objvar` | O(E · AST_size) |
| C4: Not in any inequality | ✓ Yes | `edef.relation` filter | O(E · AST_size) |
| C5: Chain consistency | ✗ No | Requires symbolic analysis of reduced KKT system | O(V³) or higher |

**Conclusion:** C1–C4 are statically computable without a runtime dependency graph. C5 requires
reasoning about the consistency of forced multiplier values in the reduced system, which is not
feasible statically without building a dependency graph and checking for contradictions.

**Implementation complexity for C1–C4:** ~40–60 lines of Python in `src/kkt/stationarity.py`.
No new data structures required; the existing `_collect_referenced_variable_names` pattern is
directly reusable.

---

## 4. False Positive Risk Assessment

### Models Tested

The following currently-solving models were checked against criteria C1–C4 (original) and
C1–C4 (tightened, with C3 requiring v appear in E_obj):

| Model | Candidates (original C1–C4) | Pass tightened C3? | Would Be Excluded | Risk |
|-------|-----------------------------|--------------------|-------------------|------|
| **ajax** | 0 | — | — | None |
| **blend** | 0 | — | — | None |
| **trnsport** | 0 | — | — | None |
| **rbrock** | 0 | — | — | None |
| **prodmix** | 0 | — | — | None |
| **mathopt2** | 0 | — | — | None |
| **himmel11** | 3 (`g2`, `g3`, `g4`) | ✗ No — vars don't appear in E_obj at all | No | Safe |
| **house** | 3 (`a1`, `a2`, `l`) | ✗ No — vars appear in chained EQ eqs, not E_obj | No | Safe |
| **demo1** | 4 (`revenue`, `mcost`, `labcost`, `labearn`) | ✓ Yes — vars appear in `income` (E_obj) | YES — **FALSE POSITIVE** | Would break model |

**Result of tightening C3:** himmel11 and house are correctly excluded from the candidate set.
Only demo1 remains as a false positive under C1–C4 (tightened).

### Why C1–C4 (Tightened) Are Still Insufficient: demo1 vs mexss

demo1 and mexss have structurally identical patterns:
- Both are LP models
- Both have scalar free variables defined by a single `=E=` equation
- Both have those variables appearing only in the objective-defining equation
- Both produce stationarity equations of the form `±1 + nu_eqn = 0`

Yet demo1 **solves correctly** and mexss **fails**. The key difference lies in how the forced
multiplier values interact with the rest of the system:

- **demo1**: The forced values (`nu_arev=1`, `nu_acost=-1`, etc.) appear in `stat_xcrop`,
  which is then balanced by `lam_landbal` and `lam_laborbal`. The system is consistent.
- **mexss**: The forced values (`nu_apsi=-1`, `nu_alam=-1`, etc.) appear in `stat_u`,
  `stat_e`, `stat_v`. These, combined with the LP complementarity slackness conditions for
  the inequality constraints (`comp_mbf`, `comp_mbr`, etc.), produce an over-determined
  system that PATH cannot satisfy.

**This inconsistency is not detectable from structural analysis of the IR alone.** It requires
either: (a) running the solver and observing infeasibility, (b) building a dependency graph and
checking whether the forced multiplier values create contradictions with complementarity conditions,
or (c) a domain-specific rule that identifies variables that parameterize the objective function
without contributing to any binding constraint.

### False Positive Risk Summary

**With tightened C3 (requiring v appear in E_obj), applying C1–C4 to all currently-solving
models would incorrectly exclude 4 optimization variables in demo1, breaking that model.**
himmel11 and house are safe (their candidate variables fail tightened C3). The test suite
would catch the demo1 regression automatically (pipeline solve test), but the false exclusion
would still produce a wrong MCP formulation. C5 is still required to distinguish demo1 from
mexss.

---

## 5. Conservative vs. Aggressive Heuristic Recommendation

### Option A: Aggressive (C1–C4 with original C3)
Detect and exclude any variable passing all four structural criteria (C3 allows variables
that appear in no other equation).

- **Pros:** Simple, statically computable, O(E·V) cost, ~50 lines of code.
- **Cons:** **High false positive risk.** Would break demo1, himmel11, house. Not safe.
- **Verdict:** ❌ Do not implement.

### Option B: C1–C4 with tightened C3 (requires v appear in E_obj)
Apply C1–C4 with the revised C3: v must appear in E_obj (not just "appears nowhere else").

- **Pros:** Correctly handles mexss pattern. himmel11 and house are safe (vars fail tightened C3).
  Reduces false positive set from 3 models to 1.
- **Cons:** demo1 still a false positive — its accounting vars appear in `income` (E_obj) just
  like mexss vars appear in `obj`. C5 is still required to distinguish the two cases.
- **Verdict:** ⚠️ Better, but still insufficient without C5.

### Option C: Deferred to Sprint 21 (Recommended)
Do not implement accounting variable detection in Sprint 20. Instead:
1. Document the mexss failure mode precisely (this document).
2. Tag mexss as a known limitation requiring architectural investigation.
3. In Sprint 21, design a proper dependency-graph-based approach that can
   check multiplier consistency before excluding variables.

- **Pros:** Zero regression risk. No false positives. No rushed implementation.
- **Cons:** mexss remains infeasible through Sprint 20.
- **Verdict:** ✅ **Recommended for Sprint 20.** mexss is a single model; the cost of
  getting accounting variable detection wrong (silently breaking demo1, himmel11, house)
  is higher than the cost of leaving mexss infeasible for one more sprint.

### Proposed Sprint 21 Algorithm (for future design)

The correct detection algorithm requires a 5th criterion based on **objective contribution
reachability**:

```
v is an accounting variable if:
  C1: Scalar VarRef LHS of exactly one =E= equation E_def(v)
  C2: v not on RHS of E_def(v)
  C3: v's only non-defining equation reference is E_obj (objective-defining eq)
  C4: v not in any inequality constraint
  C5: The stationarity expression for v, after forced substitution of multiplier
      values, does not create a contradiction with any complementarity condition
      — verified by building a constraint dependency graph on the KKT system
```

C5 can be approximated by: **the RHS of E_def(v) must contain only parameters or other
accounting variables** (no direct optimization variables). This ensures the chain of forced
multiplier values terminates cleanly without reaching optimization-variable stationarity
equations.

---

## 6. Implementation Location

**File:** `src/kkt/stationarity.py`
**Function:** `build_stationarity_equations` (line 487)
**Location within function:** After the existing `_collect_referenced_variable_names` filter
(line ~534), add a second filter:

```python
# After line ~539 (referenced_vars filter):
accounting_vars = _detect_accounting_variables(kkt.model_ir)
var_groups = {
    name: insts for name, insts in var_groups.items()
    if name.lower() not in accounting_vars
}
```

**New function:** `_detect_accounting_variables(model_ir: ModelIR) -> set[str]`
in the same file, parallel to `_collect_referenced_variable_names`.

**Emitter impact:** The MCP emitter must also:
1. Not include excluded accounting vars in the MCP pairing block
2. Not declare their `piL`/`piU` multipliers
3. Still include the original defining equations (they remain as equality constraints
   paired with their `nu_*` multipliers)

---

## 7. Corpus-Wide Impact Estimate

- **Models with any `=E=` equation:** 214 of 219 (97.7%)
- **Models with `=E=` + `sum(` patterns:** 176 of 219 (80.4%)
- **Models matching C1–C4 (accounting var candidates):** mexss + demo1 + himmel11 + house
  confirmed; exact corpus-wide count not computed (full scan exceeds 2-minute timeout)
- **Models currently failing that would be fixed by correct accounting var detection:**
  mexss (1 model; model_status=5, Locally Infeasible)
- **Models currently solving that would be broken by C1–C4 naive implementation:**
  3 (demo1, himmel11, house)

The pattern is common enough that a correct implementation would likely help additional
models beyond mexss, but the false positive risk requires the C5 constraint to be
implemented first.

---

## 8. Summary of Findings for KNOWN_UNKNOWNS

### Unknown 2.1: mexss Accounting Variable Pattern
**VERIFIED** — mexss has exactly 4 accounting variables: `phipsi`, `philam`, `phipi`, `phieps`.
All are scalar free variables. Each appears as the LHS of exactly one `=E=` equation and nowhere
else except the objective-defining equation `obj`. All four match C1–C4.

### Unknown 2.2: Static IR Analysis Feasibility
**VERIFIED** — C1–C4 are statically computable from `ir.equations` and `ir.objective`.
No runtime dependency graph is needed for detection. However, C5 (correctness verification,
preventing false positives) requires a deeper analysis not available from static IR.
**Recommendation: defer to Sprint 21** until a safe C5 can be formulated.

### Unknown 2.3: Corpus-Wide Model Count
**PARTIALLY VERIFIED** — mexss is the only currently-failing model confirmed to be unblocked by
correct accounting var detection. At least 3 additional currently-solving models (demo1,
himmel11, house) have the same structural pattern and would be affected by any implementation.
Full corpus count not computed due to scan timeout.

### Unknown 2.4: False Positive Risk
**VERIFIED — MODERATE RISK.** With the original C3, applying C1–C4 would incorrectly exclude
10 variables across 3 currently-solving models (demo1, himmel11, house). With tightened C3
(requiring v appear in E_obj), only demo1 (4 vars) remains a false positive. The test suite
(pipeline solve tests) would catch regressions automatically. Safe implementation requires C5
to distinguish demo1 from mexss.

---

## Appendix: Data Sources

| Source | Usage |
|--------|-------|
| `data/gamslib/raw/mexss.gms` | Original model structure, variable/equation declarations |
| `data/gamslib/gamslib_status.json` | mexss current status (Locally Infeasible, model_status=5) |
| `data/gamslib/mcp/mexss_mcp.gms` / `/tmp/mexss_mcp.gms` | Generated MCP, stationarity equations |
| `src/kkt/stationarity.py:487` | `build_stationarity_equations` — implementation location |
| `src/kkt/stationarity.py:55` | `_collect_referenced_variable_names` — parallel detection function |
| `data/gamslib/raw/demo1.gms` | False positive case (LP, same pattern, currently solves) |
| `data/gamslib/raw/himmel11.gms` | False positive case (QCP, same pattern, currently solves) |
| `data/gamslib/raw/house.gms` | False positive case (NLP, same pattern, currently solves) |
| `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` | Issue background |
