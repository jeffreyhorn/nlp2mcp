# Priority 9 — KKT-Residual Verification Harness Design (PR27)

**Task:** Sprint 28 Prep Task 4 (design spec only — the harness is *built* in-sprint, Days 1–3)
**Date:** 2026-06-11
**Deliverable script (to be built):** `scripts/diagnostics/kkt_residual.py`
**Purpose:** Formalize Sprint 27's GDX warm-from-good-optimum experiment into the standard **Case-(a/b/c) emit-bug-vs-non-convexity discriminator** that the Phase-0 `### Verification Methodology` gate references (PR27). Three of the six Sprint 28 carryforwards (#1224 mine, #1388 camshape, #1390 kand) need exactly this at their Phase-0 gate.

---

## 1. CLI Interface

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py <model.gms> [--gdx <solution.gdx>] [--tol 1e-6] [--json <out.json>] [--nlp-solver <name>] [--no-cold-start]
```

| Argument | Required | Meaning |
|---|---|---|
| `<model.gms>` | yes | The source NLP model (the same file the pipeline translates). |
| `--gdx <solution.gdx>` | no | A pre-solved NLP solution (primals + marginals). If omitted, the harness solves the NLP first. |
| `--tol <float>` | no (default `1e-6`) | Per-row residual tolerance separating Case b from Case c. |
| `--json <out.json>` | no | Write the machine-readable report to this path (human summary always goes to stdout). |
| `--nlp-solver <name>` | no (default `CONOPT`) | NLP solver for the no-`--gdx` path. |
| `--no-cold-start` | no (flag) | Skip the optional cold-start MCP solve used to split Case a from Case c (§3); report the residual + Case b/guard only. Use when only the stationarity residual is wanted (faster). |

**Pipeline (no `--gdx`):**

1. Solve the NLP (`<model.gms>`) → obtain primals (`.l`) and constraint/bound marginals (`.m`).
2. Emit the MCP (reuse `src/emit/emit_gams.py`, the same path the pipeline uses).
3. **Warm-start** the MCP: set every primal variable `.l` from the NLP solution and every multiplier variable `.l` from the transferred duals (§2).
4. Run the MCP with `iterlim=0` (PATH evaluates the system at the start point without iterating) → read each row's residual from the listing / a residual-only evaluation.
5. Classify (§3), emit the report (§4).

**Pipeline (`--gdx`):** skip step 1 — load primals + marginals from the GDX via `execute_loadpoint` / `$gdxin`. Everything else is identical. This is the practical path for slow NLPs (Unknown 9.3): `--gdx` makes the harness independent of NLP solve time.

`iterlim=0` (residual-only) is what makes the harness fast and side-effect-free: it never tries to *solve* the MCP, only to *evaluate* whether the warm-start point is a zero of the emitted system.

---

## 2. Dual-Transfer Mechanism (Unknown 9.1)

The harness transfers each NLP constraint/bound marginal into the corresponding MCP multiplier variable's `.l`, then checks whether the stationarity rows vanish there. The multiplier↔equation correspondence is already known to the emitter (`src/kkt/naming.py`, `src/kkt/complementarity.py`), so the transfer is driven from the same mapping rather than re-derived.

### Multiplier classes (from `src/kkt/naming.py`)

| NLP object | MCP multiplier | Sign / pairing | Transfer source |
|---|---|---|---|
| Equality constraint `eq` | `nu_<eq>` (free) | paired as the equality row | NLP `eq.m` |
| Inequality constraint `eq` | `lam_<eq>` (≥ 0) | paired with a `comp_ineq` complementarity row | NLP `eq.m` (abs value; sign normalized to the emitted `=g=`/`=l=` orientation) |
| Lower bound on `v` | `piL_<v>` / `piL_<v>_<idx>` (≥ 0) | paired with `comp_bounds_lo` | NLP `v.m` where `v.l ≈ v.lo` |
| Upper bound on `v` | `piU_<v>` / `piU_<v>_<idx>` (≥ 0) | paired with `comp_bounds_up` | NLP `v.m` where `v.l ≈ v.up` |

### The inequality → `comp_*` generalization (the Day-9 `pwl_m`/`pwu_m` pattern)

In Sprint 27 (Day 9, launch) inequality/bound marginals were transferred by hand: the NLP `.m` values were loaded into helper parameters (`pwl_m`/`pwu_m`) and then assigned into the multiplier variables that the `comp_*` rows pair against. The harness **generalizes this for every multiplier class**:

1. Capture the NLP solution's marginals into a GDX (`<v>.m`, `<eq>.m`).
2. For each emitted multiplier variable, look up its paired constraint/bound via the `build_complementarity_pairs` mapping (`comp_ineq` keyed by eq name; `comp_bounds_lo`/`comp_bounds_up` keyed by `(var, indices)`; `equality_eqs` for `nu_*`).
3. Load `<eq>.m` / `<v>.m` into the multiplier `.l`, applying the sign convention below.

### Sign / recovery conventions (Unknown 9.1 Q3)

- `nu_<eq>` (equality): free; load the NLP `eq.m` directly (the stationarity assembly's sign is fixed by the Lagrangian orientation the emitter already uses).
- `lam_<eq>` (inequality): GAMS `=g=`/`=l=` marginals carry a sign tied to the constraint orientation; normalize to the non-negative convention the `comp_ineq` row expects (`lam ≥ 0`, slack ≥ 0). The harness reads the emitted constraint orientation to pick the sign.
- `piL_<v>` / `piU_<v>` (bounds): recovered from `v.m` at the solution — `piL` is the positive part of `v.m` on a lower-active bound (`v.l ≈ v.lo`), `piU` the magnitude on an upper-active bound (`v.l ≈ v.up`); inactive bounds get `0`.

### Reuse of the `--nlp-presolve` machinery (Unknown 9.1 Q4)

The existing `_emit_nlp_presolve` path (`src/emit/emit_gams.py`) already `$include`s the source NLP and warm-starts the MCP **primals**. The harness reuses that for primal transfer and adds the **dual** transfer above (presolve does not load `.m` into the multipliers). This keeps the harness aligned with the production emit rather than maintaining a parallel warm-start.

### Consistency self-check (the dual-transfer's own validity)

Before trusting any *stationarity* residual, the harness verifies the **constraint / complementarity rows** are ≈ 0 at the transferred point (the primal feasibility + complementary slackness the NLP solution already satisfies). If a constraint row is non-zero, the *transfer* is wrong (not the emit), and the harness reports `dual_transfer_inconsistent` instead of a Case verdict — this is the guard Unknowns 5.2 and 9.1 demand (a bad transfer must never masquerade as a Case-b emit bug).

---

## 3. Case-(a/b/c) Verdict Logic (Unknown 9.2)

**First** run the §2 dual-transfer self-check; only if it passes (all constraint / complementarity rows ≈ 0) does the verdict proceed. Then evaluate the **stationarity rows** (`stat_*`) at the transferred NLP KKT point. Let `max|r|` be the largest absolute **stationarity** residual and `tol` the threshold (default `1e-6`). Complementarity / constraint rows are **not** part of `max|r|` — they are the §2 consistency guard; if any exceeds `tol`, the harness returns `dual_transfer_inconsistent` instead of a Case verdict. So Case b is triggered by a stationarity violation only.

| Verdict | Condition | Meaning | Fix path |
|---|---|---|---|
| **Case a** | `max|r| ≤ tol` AND a **cold-start** MCP solve reaches `model_optimal` matching the NLP | Emitted KKT is correct and PATH converges | none — model is healthy |
| **Case b** | `max|r| > tol` (some stationarity row non-zero at the NLP KKT point) | **Emit bug** — the emitted stationarity is mathematically wrong | fix the emit; the **max-residual row is the prime-suspect term** |
| **Case c** | `max|r| ≤ tol` BUT a cold-start MCP solve **diverges** (MS 5 / no convergence) | **Non-convexity** — the KKT point is valid but PATH can't reach it cold | warm-start (or solver change), **not** an emit fix |
| **(guard)** | a *constraint* row exceeds `tol` | dual transfer inconsistent (§2) | fix the transfer, re-run — not a model verdict |

**Threshold calibration (Unknown 9.2 Q1) — calibration *targets* grounded in Sprint 27 ground truth, to be reproduced when the harness is built (the residual figures below are the Sprint 27 historical measurements, not a run of this harness):**

- camshape — Sprint 27 `stat_r(i1)` INFES ≈ 396 ≫ `1e-6` → **Case b** (matches the Day-11 manual classification).
- launch — Sprint 27 proved 2257.80 a valid KKT point (residual ≈ 0) → **Case a** (after the #1378 double-apply fix) / the pre-fix corrupted objective showed a non-zero residual → **Case b** before the fix.
- cclinpts — Sprint 27 residual-verified the eliminated-KKT max|r| = 5e-8 at the NLP optimum, yet cold PATH converges to a spurious degenerate point → **Case c** (non-convex; needs warm-start). This is the canonical Case-c calibration point.

`tol = 1e-6` cleanly separates the camshape Case-b (≈ 396) from the cclinpts Case-c (5e-8); it is `--tol`-tunable for models with looser numerics.

**Case-c detection (Unknown 9.2 Q2):** distinguishing Case c from Case a requires the cold-start comparison — the harness optionally runs a second MCP solve from the *default* start (not warm-started) and checks whether PATH still reaches the NLP optimum. If `max|r| ≤ tol` but cold PATH diverges, it is Case c. (Skippable via `--no-cold-start` when only the residual is wanted — the harness then reports the residual + Case b / `dual_transfer_inconsistent` only, leaving the a-vs-c split unresolved.)

---

## 4. Output Format (Unknown 9.2 Q3)

**Human summary (stdout):**

```
model: camshape    tol: 1e-6
dual transfer: CONSISTENT (max constraint residual 4.1e-09)
verdict: CASE B  — EMIT BUG
max-residual row: stat_r('i1')   |r| = 3.96e+02
top rows:
  stat_r('i1')   3.96e+02
  stat_r('i2')   1.12e+01
  stat_x('i1')   2.0e-08
```

**Machine-readable (`--json`):**

```json
{
  "model": "camshape",
  "tol": 1e-6,
  "dual_transfer": {"consistent": true, "max_constraint_residual": 4.1e-09},
  "verdict": "case_b",
  "verdict_label": "emit_bug",
  "max_residual_row": {"name": "stat_r", "index": ["i1"], "residual": 396.0},
  "rows": [
    {"name": "stat_r", "index": ["i1"], "residual": 396.0, "kind": "stationarity"},
    {"name": "stat_x", "index": ["i1"], "residual": 2.0e-08, "kind": "stationarity"}
  ]
}
```

The JSON is what Phase-0 gates cite as evidence; the `max_residual_row` is the Day-0 trace's prime-suspect surface (PR24).

---

## 5. Phase-0 "Verification Methodology" Command String

The canonical command Tasks 3 and 5 reference (already wired into the CONTRIBUTING.md Phase-0 template under PR27):

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py <model.gms> --gdx <model_nlp_solution.gdx> --tol 1e-6 --json phase0_<model>.json
```

A Phase-0 PROCEED cites the resulting `verdict` + `max_residual_row` as the traced fix-surface evidence (Case b ⇒ proceed with the emit fix at the max-residual row; Case c ⇒ REPLAN toward warm-start, not an emit change).

---

## 6. First-Consumer Invocation Sketches

### mine (#1224 — parameter-valued-offset cross-term)

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms --gdx mine_nlp.gdx --json phase0_mine.json
```

**Expected:** `dual transfer CONSISTENT`; **Case b** with the max-residual row in `stat_x(l,i,j)` — the non-inverted `sum(k, lam_pr(k,l,i,j))` should leave a non-zero residual that the corrected inverse-offset form (`sum(k, lam_pr(k,l,i-li(k),j-lj(k))) − sum(k, lam_pr(k,l-1,i,j))`) drives to ≈ 0. Also confirms boundary cells (Unknown 1.3): if the residual is non-zero *only* at offset-out-of-domain cells, the fix needs a domain guard rather than the inversion.

### camshape (#1388 — Case-(b) `stat_r` divergence)

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camshape.gms --gdx camshape_nlp.gdx --json phase0_camshape.json
```

**Expected:** `dual transfer CONSISTENT` (the #1424 subset-default fix landed in Sprint 27 makes the 10-symbol warm-start valid); **Case b** with `stat_r('i1')` ≈ 396 as the max-residual row — reproducing the Day-11 §4.6 manual classification and pinning the per-term hand-derivation target (`stationarity.py:1835`). Unknown 2.2's blast-radius check is downstream (golden-staleness, Task 7).

### kand (#1390 — re-diagnosis; tree-conditioned duals)

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/kand.gms --gdx kand_nlp.gdx --json phase0_kand.json
```

**Expected:** the **dual-transfer consistency self-check is the gating step** (Unknown 5.2) — kand's `lam_dembalx` multipliers are `tree(nn,n)`-conditioned aliased Sums; the harness must load the NLP `dembalx` marginals respecting the tree predicate and confirm the *constraint* rows are ≈ 0 first. Only then is the `stat`-row verdict (Unknown 5.1: 195-vs-2613 gap) trustworthy. If transfer is consistent and `max|r| ≤ tol` → **Case c** (the gap is non-convexity / LP-recourse coupling, → Sprint 29 REPLAN); if a `stat` row exceeds tol → **Case b** (a localizable emit row, in-sprint fix).

---

## 7. Validation-Against-Known-Cases Plan

Before the harness is trusted in-sprint, it must reproduce the Sprint 27 manual classifications:

| Model | Expected verdict | Sprint 27 reference |
|---|---|---|
| launch (post-#1378) | Case a (residual ≈ 0) | Day 9 — 2257.80 proven a valid KKT point |
| camshape | Case b (`stat_r('i1')` ≈ 396) | Day 11 — §4.6 discriminator |
| cclinpts | Case c (max\|r\| = 5e-8, cold PATH diverges) | Day 6 — eliminated-KKT residual verification |

Reproducing all three (one per case) calibrates `tol` and confirms the dual transfer + verdict logic before any carryforward leans on it.

---

## 8. Runtime / `--gdx` Mitigation (Unknown 9.3)

- Fast models (mine, camshape): the no-`--gdx` path (solve NLP + residual eval) is practical (seconds–low minutes).
- Slow NLPs (kand, ganges ~8 min): require `--gdx` with a pre-solved solution so the harness never re-solves; the residual evaluation itself is `iterlim=0` and near-instant.
- The `--gdx` and solve-NLP paths must produce the **same** residual on a fast model (the 9.3 acceptance check) — otherwise the GDX load is dropping primals/duals.
