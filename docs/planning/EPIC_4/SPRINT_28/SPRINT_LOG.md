# Sprint 28 Log

**Sprint:** 28 (Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling)
**Plan:** `PLAN.md` · **Prompts:** `prompts/PLAN_PROMPTS.md` · **Baseline:** `BASELINE_METRICS.md`
**Day-0 baseline (= Sprint 27 final):** Parse 142 · Translate 135 · Solve 105 · Match 62 · model_infeasible 8 · path_syntax_error 8 · Tests 4,779.
**Targets:** Solve ≥ 110 (stretch; firm → 109) · Match ≥ 65 · model_infeasible ≤ 5 · Tests ≥ 4,800 · determinism ×3 seeds.

## Cumulative Metrics Tracker

| Metric | Day 0 | Day 5 (CP1) | Day 10 (CP2) | Day 13 (final) | Target |
|---|---|---|---|---|---|
| Solve | 105 | — | — | — | ≥ 110 (stretch) |
| Match | 62 | — | — | — | ≥ 65 |
| model_infeasible | 8 | — | — | — | ≤ 5 |
| Tests | 4,779 | — | — | — | ≥ 4,800 |

---

## Day 0 — Kickoff + Day-0 Traces (2026-06-12)

**Status:** 🟢 DONE — baseline confirmed, golden refresh landed, Day-0 structural localizations recorded in all six Phase-0 gates, PR25 tally restated. No `src/` fix (trace + setup only).

### Baseline confirmation
- `git diff 68be9cca..HEAD -- src/ scripts/` is **empty** — no pipeline-affecting change since the Sprint 27 Day-13 close (only Sprint 28 prep docs, PRs #1428–#1437). **Sprint 28 Day 0 = Sprint 27 final** holds; reused the committed `gamslib_status.json` (no fresh ~4 h retest).

### One-time golden refresh (Priority 8 prep)
- Regenerated the 4 drifted presolve goldens (`camshape`/`cesam`/`fawley`/`korcge` `_mcp_presolve.gms`) so the golden-staleness CI gate (built Day 12) starts clean. Byte-stable on re-emit (PR12); `make test` 4,779 passed (no test pins these goldens). Single reviewable commit (`3400b3ba`).
- **Stale-assumption flagged:** the prompt's `make regen-goldens` target is a Priority-8 / Day-12 deliverable and does **not** exist yet — used the canonical `python -m src.cli <raw> -o <golden> --quiet --nlp-presolve` directly (equivalent).

### Day-0 structural localizations (PR24 — lightweight, harness-residual confirmation per priority day)
- **Stale-assumption flagged:** the KKT-residual harness (the PR24 evidence tool) is a Priority-9 / Days-1–3 deliverable and does **not** exist yet, so Day-0 traces are **structural localizations** (emit-row inspection), with each model's full Case-(a/b/c) residual confirmation scheduled on its priority day (per `PLAN.md` §16). Each gate's `Traced Fix-Surface (Day-0)` line is filled with a **candidate** surface.

| Issue | Localization | Verdict |
|---|---|---|
| #1224 mine | `stat_x(l,i,j)` (`mine_mcp.gms:103`) carries the **non-inverted** `sum(k, lam_pr(k,l,i,j))` — no offset inversion, no `l-1` term | Confirms prep (row pinned; build site Day 4) |
| #1388 camshape | `stat_r(i)` (`:421`) guards `lam_convexity(i±1)` by `middle(i)` + the looser `ord(i)>1`/`ord(i)<=card(i)-1`, **not** the canonical `middle(i±1)` | Confirms prep (Day 5) |
| #1393 otpop | `stat_p(tt)` + `stat_x(tt)` both carry the over-counted `sum(t__, … nu_kdef)$(t(tt))` | Confirms prep (Days 6–7) |
| **#1335 otpop** | **HYPOTHESIS REFINED:** `nu_zdef` **is present** in `stat_x` (the `card(t)-ord(t)` offset *does* evaluate for ∂/∂x) and is missing **only from `stat_p`** — the `∂zdef/∂p` cross-term is the dropped one, not a blanket evaluator gap | **Corrects prep** (Days 6–7) |
| #1387 cclinpts | `stat_fb(j)` (`:128`) has only the Term-2-at-j contribution — **missing 3 of 4** hand-derived terms (the `j+1` cross-terms); `stat_b(j)` lacks Term-2-at-j+1 | Confirms Day-6 diagnosis (Days 8–9) |
| #1390 kand | 21 phantom-offset `lam_dembalx(j,t+1,n±k)` terms present in `stat_y` — but **proven inert** (Sprint 27); **no alternative emit surface evident** | Re-diagnose Day 10 (harness Case-b/c) |
| camcge | `camcge_mcp.gms` emits a **structurally complete** KKT (37 `stat_*` + 10 `comp_*`, no missing row) — **no emit surface**; PATH-side per Sprint 27 | Confirms gate premise (Day 11) |

**Headline Day-0 finding:** the #1335 premise is **partially wrong** (the offset evaluates for ∂/∂x; only ∂/∂p is dropped) — exactly the prep-surface-correction PR24 exists to catch. All other prep hypotheses are structurally confirmed at the row level.

### PR25 Day-0 projection tally (genuine bucket-to-success vs bucket-forward)
- **Solve (105 → target ≥ 110 stretch):** genuine gains = mine +1, camshape +1, otpop +1 (firm) → **108**; camcge +1 **conditional** → 109. The +5th to 110 is a stretch with no carryforward backing. cclinpts/kand already solve → **Match-only, 0 Solve credit**.
- **Match (62 → target ≥ 65):** genuine gains = otpop +1, cclinpts +1, kand +1 (firm) → **65** (meets). mine/camshape Match **conditional** on solving first → stretch.
- **Bucket-forward (progress, not target credit):** camcge if it stays `model_infeasible` (degeneracy); #1374/#1400/#1385 cleanups (no bucket transition).

### Deliverables
- `data/gamslib/mcp/{camshape,cesam,fawley,korcge}_mcp_presolve.gms` refreshed (commit `3400b3ba`).
- `Traced Fix-Surface (Day-0)` filled in `ISSUE_{1224,1388,1393,1335,1387,1390,1330}_*.md` (candidate surfaces).
- This Day-0 SPRINT_LOG entry.

### Day-0 addendum — golden-refresh review investigation (presolve emit)

The PR #1438 review (Copilot) raised two `--nlp-presolve` concerns on the refreshed goldens. Both **investigated empirically** (full GAMS solve): **neither is a sprint blocker**, and the refresh introduced neither (faithful regen; old goldens had the same patterns).

- **korcge ordering — REAL latent emit bug, filed #1439.** The `--nlp-presolve` variant aborts (EXECERROR=5): `it(i)=yes$(e.l or m.l)` + the `.fx` fixups run **before** the `$include` with `.l=0`, so `it` is empty and vars fix to 0 → `1/xxd(i)`/`m(i)**(-rhoc)` div-by-zero. **Not blocking:** korcge solves **MODEL STATUS 1 Optimal** via the non-presolve file (`mcp_file_used = None`); the presolve variant is unused for its metrics; old golden was already broken (Locally Infeasible). Filed `ISSUE_1439_*.md` + GitHub #1439, wired into `PLAN.md`/`PLAN_PROMPTS.md` Day 0 + Day 12 (Priority 10 divergence detector). The reviewer correctly identified the mechanism.
- **cesam empty `nu_*` transfer — BENIGN, no issue filed.** Despite the empty equality-multiplier warm-start, cesam's presolve MCP solves to **MODEL STATUS 1 Optimal** (primal + `piL_*`/`piU_*` bound-multiplier transfer suffices). Side-finding: cesam solves under presolve but is Infeasible under non-presolve (its pipeline path) — possibly recoverable via presolve; noted for the Priority 2/3 cesam2 work.

---

## Day 1 — KKT-Residual Harness build (start) (2026-06-12)

**Status:** 🟢 DONE — CLI + dual-transfer reuse/extraction + residual-only rewrite + consistency self-check landed (`scripts/diagnostics/kkt_residual.py`) with 16 unit tests; `make test` 4,795 passed (+16).

### Architecture decision: **A — reuse the `--nlp-presolve` emit** (design §2.66 corrected, PR24)

The design's §2.66 premise — *"presolve does not load `.m` into the multipliers"* — is **empirically false**: `_emit_nlp_presolve` (`src/emit/emit_gams.py:1067–1130`) already generates the complete dual transfer (`nu_<eq>.l = eq.m`, `lam_<eq>.l = abs(eq.m)`, `piL_*`/`piU_*` from variable marginals), confirmed in `launch_mcp_presolve.gms`. So the harness **reuses** the production transfer rather than re-deriving it via `build_complementarity_pairs` — simpler, DRY, production-aligned, and the consistency self-check catches any transfer gaps (e.g. cesam's empty `nu_*`, korcge #1439). User approved A. Design doc §2 annotated with the correction.

### Built (Day 1)

- `scripts/diagnostics/kkt_residual.py` — the CLI (`<model.gms> [--gdx] [--tol 1e-6] [--json] [--nlp-solver] [--no-cold-start]`); `emit_warmstarted_mcp` (reuse `translate_single_model(..., nlp_presolve=True)`); `extract_dual_transfer` (parse the four multiplier classes from the emit); `make_residual_only` (insert `mcp_model.iterlim = 0;` before the `Solve` → residual-only evaluation); `classify_consistency` (the §2 self-check → `dual_transfer_inconsistent`).
- `tests/unit/diagnostics/test_kkt_residual_harness.py` — 16 unit tests. The **dual transfer on launch** check uses the committed `launch_mcp_presolve.gms` golden (no GAMS): extracts **nu=8, lam=2, piL=13, piU=6** (all four classes; `lam_*` use `abs()`).
- `make typecheck`/`format`/`lint` clean (harness file ruff/black/mypy-clean; the only mypy notes are pre-existing in transitively-imported `scripts/gamslib/db_manager.py`, outside the gate scope).

### Next: Day 2 — Case-(a/b/c) verdict + JSON/human output (run the residual-only MCP via GAMS, parse per-row residuals, apply the self-check then the verdict).

---

## Day 2 — KKT-Residual Harness build (verdict + output) (2026-06-13)

**Status:** 🟢 DONE — full pipeline (GAMS run + gdxdump parse + §2 self-check + relative-residual Case-(a/b/c) verdict + JSON/human output + `--gdx`) landed in `scripts/diagnostics/kkt_residual.py`; 71 new unit tests (87 total) + 1 GAMS-gated e2e; end-to-end self-validated on launch. **Four empirical findings (PR24) reshaped the build before any code — verified with real GAMS runs, not assumed.**

### PR24 findings (design §2/§3/§7 corrected; user approved the relative-residual approach)

1. **`nu` sign flip (🔴 architectural).** Architecture A's premise — that reusing the `--nlp-presolve` warm-start puts the MCP at a KKT zero — is **false**: the production `nu_<eq>.l = eq.m` is sign-flipped vs the emitted stationarity convention. launch `stat_aweight.L = 16.09 = 2·|eq.m|`; `nu = -eq.m` drops every stationarity residual to ~1e-12. Fix: `apply_residual_sign_correction` negates `nu_*` for the residual-only variant (`lam`/`piL`/`piU` load as non-negative magnitudes, untouched). Not a production bug (PATH iterates past it).
2. **Relative residual (🟡, the verdict core).** After the `nu` fix, launch is clean except `stat_ethrust ≈ 7.9e-3` — the embedded NLP's gradient-optimality tolerance (ethrust≈747). A fixed absolute `tol=1e-6` mis-flags launch as Case b. Adopted a **relative** residual `|F|/dual_scale` (`dual_scale = max(1, max|multiplier|)`, IPOPT-style); default **`tol=1e-3`** (was `1e-6` absolute). Separates the cases by orders of magnitude.
3. **Val-vs-bounds residual (🔴 correctness).** The raw equation `.L` is the *activity*, not the residual — GAMS moves a constraint's constant to the `.LO`/`.UP` bound (`comp_up_vt`: `50000 - vt =G= 0` → Val=−vt, Lower=−50000 → feasible). Reading only `.L` falsely flagged `comp_up_vt` and the apparent `costdef`/`dweight` "discrepancies" (Finding-3-from-Day-0 **dissolved**: Val==Lower==Upper → residual 0). Fix: extract via `gdxdump … CSVAllFields` and compute residual/infeasibility from `Val` vs `[Lower, Upper]`; the complementarity guard is **relative** (`infeasibility/primal_scale`).
4. **launch is Case c, not Case a (🟡 calibration).** End-to-end: launch residual ≈ 0 (max rel ~1.4e-16), self-check CONSISTENT — **but the cold non-presolve `launch_mcp.gms` solves MODEL STATUS 5 Locally Infeasible** (obj 526, not 2257.80), so cold PATH can't reach the valid KKT point → **Case c** by the §3 definition. The §7 table conflated "residual ≈ 0" with Case a; corrected. A clean Case-a calibration model still needs picking on Day 3; launch is a *second* Case-c example.

### Built (Day 2)

- Residual extraction: `apply_residual_sign_correction`, `inject_residual_unload` (`execute_unload` after the `iterlim=0` Solve), `parse_gdxdump_allfields` (Val/Lower/Upper), `RowResidual` (Val-vs-bounds `signed_residual`/`infeasibility`), `dual_scale`/`primal_scale`/`relative_residual`.
- Verdict + output: `check_dual_transfer` (fail-closed on NaN/inf + relative gross-infeasibility guard; equality residuals informational), `classify_verdict` (relative residual; cold-start `optimal`/`diverged`/`unavailable` → Case a/c/`case_a_or_c`), `build_report`/`format_json`/`format_human`.
- GAMS orchestration: `find_gams_tools`, `run_gams` (from `PROJECT_ROOT`), `gdxdump_equation`/`gdxdump_symbol`, `collect_residuals`/`collect_multiplier_values`, `cold_start_status` (reuses `solve_mcp`), `run_harness`, rewritten `main()` (only `--nlp-solver` still deferred).
- `--gdx`: `neutralize_nlp_solve` + `build_gdx_skip_variant` (repoint `$include` at a neutralized source + `execute_loadpoint`) → skips the embedded NLP solve (design §8). Text transforms unit-tested; real-GDX correctness validated Day 3+.
- Tests: 87 unit (`tests/unit/diagnostics/test_kkt_residual_harness.py`) + 1 GAMS-gated e2e (`tests/integration/diagnostics/test_kkt_residual_e2e.py`, skips without GAMS/raw launch). Self-validated: launch → CONSISTENT, stationarity rel ~1e-16, verdict Case c.

### Next: Day 3 — validate launch/camshape/cclinpts (camshape → Case b `stat_r('i1')`; cclinpts → Case c; pick a clean Case-a model), wire the Phase-0 `### Verification Methodology` command, open the P9 PR.
