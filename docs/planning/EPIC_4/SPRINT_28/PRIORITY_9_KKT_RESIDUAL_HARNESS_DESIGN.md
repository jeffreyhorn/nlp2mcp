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
| `--tol <float>` | no (default `1e-3`, **relative**) | Relative stationarity-residual tolerance (`|F|/dual_scale`) separating Case a/c from Case b (Day-2 correction; was `1e-6` absolute). |
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
| Inequality constraint `eq` | `lam_<eq>` (≥ 0) | paired with a `comp_ineq` complementarity row | NLP `eq.m`, signed so the loaded `lam_<eq>` satisfies `lam ≥ 0` for the emitted `=g=`/`=l=` orientation |
| Lower bound on `v` | `piL_<v>` / `piL_<v>_<idx>` (≥ 0) | paired with `comp_bounds_lo` | NLP `v.m` where `v.l ≈ v.lo` |
| Upper bound on `v` | `piU_<v>` / `piU_<v>_<idx>` (≥ 0) | paired with `comp_bounds_up` | NLP `v.m` where `v.l ≈ v.up` |

### The inequality → `comp_*` generalization (the Day-9 `pwl_m`/`pwu_m` pattern)

In Sprint 27 (Day 9, launch) inequality/bound marginals were transferred by hand: the NLP `.m` values were loaded into helper parameters (`pwl_m`/`pwu_m`) and then assigned into the multiplier variables that the `comp_*` rows pair against. The harness **generalizes this for every multiplier class**:

1. Capture the NLP solution's marginals into a GDX (`<v>.m`, `<eq>.m`).
2. For each emitted multiplier variable, look up its paired constraint/bound via the `build_complementarity_pairs` mapping (`comp_ineq` keyed by eq name; `comp_bounds_lo`/`comp_bounds_up` keyed by `(var, indices)`; `equality_eqs` for `nu_*`).
3. Load `<eq>.m` / `<v>.m` into the multiplier `.l`, applying the sign convention below.

### Sign / recovery conventions (Unknown 9.1 Q3)

> **Day-2 correction (PR24, 2026-06-13):** the original claim that loading `nu_<eq>.l = eq.m` *directly* zeroes the stationarity rows is **empirically false**. Verified on launch (`iterlim=0`, `execute_unload` → `gdxdump`): the production presolve transfer `nu_<eq>.l = eq.m` leaves `stat_aweight ≈ 16.09 = 2·|eq.m|` — a **uniform sign flip** between the GAMS equality marginal and the emitted stationarity row's `nu` sign. Re-running with `nu_<eq>.l = -(eq.m)` drops **every** stationarity residual to ~1e-12 (machine zero), so launch *is* Case a once the sign is corrected. This is not a production bug (PATH iterates away from the sign-flipped dual start and still converges/matches, Sprint 27 Day 9); it is a **measurement-correctness requirement for the `iterlim=0` residual check.** The harness therefore applies a sign-correction layer (`apply_residual_sign_correction`) that negates the `nu_*` transfer for the residual-only variant. Only the **free** multiplier `nu` is sign-ambiguous; `lam`/`piL`/`piU` load as non-negative magnitudes (`abs(...)`, positive-part) with the sign carried in the emitted stationarity coefficient, so they are **not** flipped. (launch cannot confirm `lam`/`piL`/`piU` — all its inequalities/bounds are inactive at the optimum — so the Day-3 camshape validation, which has active bounds, confirms them.)

- `nu_<eq>` (equality): free; the **residual-only variant loads `-eq.m`** (the Day-2 sign correction above). Production `--nlp-presolve` loads `+eq.m` (a valid PATH warm-start, dual signs notwithstanding).
- `lam_<eq>` (inequality): GAMS `=g=`/`=l=` marginals carry a sign tied to the constraint orientation; the presolve loads `abs(eq.m)` so `lam ≥ 0` as the `comp_ineq` row expects. **Not** sign-flipped by the harness (the orientation sign lives in the emitted coefficient).
- `piL_<v>` / `piU_<v>` (bounds): recovered from `v.m` at the solution — `piL` is the positive part of `v.m` on a lower-active bound (`v.l ≈ v.lo`), `piU` the magnitude on an upper-active bound (`v.l ≈ v.up`); inactive bounds get `0`. **Not** sign-flipped.

### Reuse of the `--nlp-presolve` machinery (Unknown 9.1 Q4)

> **Day-1 correction (PR24, 2026-06-12):** this paragraph's original claim — "presolve does not load `.m` into the multipliers" — is **empirically false**. `_emit_nlp_presolve` (`src/emit/emit_gams.py:1067–1130`) **already** generates the full dual transfer (`nu_<eq>.l = eq.m`, `lam_<eq>.l = abs(eq.m)`, `piL_*`/`piU_*` from variable marginals), confirmed in `launch_mcp_presolve.gms` (nu=8, lam=2, piL=13, piU=6). **Architecture A (chosen, user-approved):** the harness **reuses the production `--nlp-presolve` emit for both primal *and* dual warm-start** — it does not re-derive the transfer via `build_complementarity_pairs`. The harness's dual-transfer layer (`extract_dual_transfer`) *verifies* the production transfer is present; the §"Consistency self-check" below catches any gap (e.g. cesam's empty `nu_*`, korcge #1439). The `build_complementarity_pairs`-driven description in this §2 is retained as the conceptual mapping but is **not reimplemented** by the harness.

The existing `_emit_nlp_presolve` path (`src/emit/emit_gams.py`) `$include`s the source NLP and warm-starts the MCP **primals and duals**. The harness reuses that whole transfer, keeping it aligned with the production emit rather than maintaining a parallel warm-start.

### Consistency self-check (the dual-transfer's own validity)

Before trusting any *stationarity* residual, the harness verifies the transferred point is sane. If it is not, the harness reports `dual_transfer_inconsistent` instead of a Case verdict — the guard Unknowns 5.2 and 9.1 demand (a bad transfer must never masquerade as a Case-b emit bug).

> **Day-2 correction (PR24, 2026-06-13):** the original "all constraint/complementarity rows ≈ 0" formulation is **too strict** — it false-positives on healthy models. Verified on launch: (1) `=g=` complementarity rows correctly carry the constraint *slack* (`comp_lo_aweight.L = 68 =` aweight−1, an inactive bound — feasible, not a violation), so a raw "≈ 0" test is wrong for inequalities; (2) the **objective-definitional and some original-equality rows are non-zero at the warm-start** (`costdef.L = -850`, `dweight.L = 20`) because the *emitted* objective/constraint expressions differ from the embedded NLP at the solution — a **separate emit-vs-embedded-NLP discrepancy** (Sprint-27 bug class), **not** a dual-transfer problem. Folding these into the transfer guard would block valid stationarity verdicts. So the Day-2 self-check is **fail-closed and conservative**: it flags `dual_transfer_inconsistent` only on (a) a **non-finite** residual anywhere (NaN/inf — e.g. the korcge #1439 div-by-zero), or (b) a **gross feasibility violation** of a complementarity row (`F < −feas_tol`, a real constraint breach). Small/moderate equality residuals are **reported** (as `max_constraint_residual`, for transparency and to surface the emit-vs-NLP discrepancy) but do **not** block the verdict. The objective-definitional row is excluded from the reported constraint set.

---

## 3. Case-(a/b/c) Verdict Logic (Unknown 9.2)

**First** run the §2 dual-transfer self-check (fail-closed: non-finite residual or gross complementarity infeasibility → `dual_transfer_inconsistent`); only if it passes does the verdict proceed. Then evaluate the **stationarity rows** (`stat_*`) at the transferred NLP KKT point.

> **Day-2 correction (PR24, 2026-06-13) — relative residual:** the design's fixed *absolute* `tol=1e-6` is **too tight for the embedded NLP's optimality tolerance.** Verified on launch (post sign-correction): all stationarity rows are ~1e-12 **except `stat_ethrust ≈ 7.9e-3`** — a genuine residual at the embedded NLP solver's gradient tolerance (`ethrust ≈ 747`, steep powers; bound inactive, so not a sign issue). An absolute `1e-6` would mis-flag launch (Case a) as Case b. The harness therefore uses a **relative stationarity residual**: `rel = |F_stat| / dual_scale`, where `dual_scale = max(1, max|multiplier value|)` over all transferred multipliers (the IPOPT-style dual-infeasibility scaling). For launch, `dual_scale ≈ 14` → `stat_ethrust` rel ≈ 5.7e-4. The default threshold is therefore **`tol = 1e-3` on the relative residual** (was `1e-6` absolute). This cleanly separates the three calibration cases by *orders of magnitude* (launch ≈ 5.7e-4 ≪ camshape ≈ O(1–10) ≫ cclinpts ≈ O(1e-9)), so the verdict is robust across `tol ∈ [1e-4, 1e-1]`; `--tol` overrides. Day-3 confirms camshape/cclinpts at this default.

Let `max|r|` be the largest **relative stationarity** residual and `tol` the threshold (default `1e-3`, relative). Complementarity / constraint rows are **not** part of `max|r|` — they are the §2 consistency guard (above). So Case b is triggered by a stationarity violation only.

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

With the Day-2 **relative** residual (`|F|/dual_scale`, default `tol = 1e-3`), the three cases separate by orders of magnitude — launch ≈ 5.7e-4 (Case a) ≪ camshape ≈ O(1–10) (Case b) and ≫ cclinpts ≈ O(1e-9) (Case c); robust across `tol ∈ [1e-4, 1e-1]`, `--tol`-tunable for models with looser numerics. (The historical figures above — camshape ≈ 396, cclinpts 5e-8 — are the Sprint-27 *absolute* measurements; the harness reports the relative residual.)

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
| launch (post-#1378) | ~~Case a~~ → **Case c** (Day-2 finding, below) | Day 9 — 2257.80 proven a valid KKT point |
| camshape | Case b (`stat_r('i1')` ≈ 396) | Day 11 — §4.6 discriminator |
| cclinpts | Case c (max\|r\| = 5e-8, cold PATH diverges) | Day 6 — eliminated-KKT residual verification |

Reproducing one per case calibrates `tol` and confirms the dual transfer + verdict logic before any carryforward leans on it.

> **Day-2 correction (PR24, 2026-06-13) — launch is Case c, not Case a.** The harness, run end-to-end on launch, confirms the stationarity residual at the NLP KKT point is ≈ 0 (max rel ~1.4e-16 after the `nu` sign correction; self-check CONSISTENT). **But the cold-start split lands Case c**, not Case a: the *cold non-presolve* `launch_mcp.gms` solves **MODEL STATUS 5 Locally Infeasible** (obj 526, not 2257.80) — cold PATH cannot reach the valid KKT point. This is internally consistent with the §3 definitions (Case a *requires* the cold solve to reach the NLP optimum) and with Sprint 27 (launch needed the presolve warm-start to match). The §7 "launch → Case a" row conflated "residual ≈ 0" with Case a; the harness correctly distinguishes them. **Consequence:** a clean Case-a calibration model still needs picking on Day 3 (a convex model whose cold MCP converges); launch serves as a *second* Case-c example. The Day-2 machinery (sign correction, Val-vs-bounds residual, self-check, relative residual, cold-start, verdict) is validated as correct by this run.

---

## 8. Runtime / `--gdx` Mitigation (Unknown 9.3)

- Fast models (mine, camshape): the no-`--gdx` path (solve NLP + residual eval) is practical (seconds–low minutes).
- Slow NLPs (kand, ganges ~8 min): require `--gdx` with a pre-solved solution so the harness never re-solves; the residual evaluation itself is `iterlim=0` and near-instant.
- The `--gdx` and solve-NLP paths must produce the **same** residual on a fast model (the 9.3 acceptance check) — otherwise the GDX load is dropping primals/duals.
