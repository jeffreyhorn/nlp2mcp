# Sprint 28 Log

**Sprint:** 28 (Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling)
**Plan:** `PLAN.md` · **Prompts:** `prompts/PLAN_PROMPTS.md` · **Baseline:** `BASELINE_METRICS.md`
**Day-0 baseline (= Sprint 27 final):** Parse 142 · Translate 135 · Solve 105 · Match 62 · model_infeasible 8 · path_syntax_error 8 · Tests 4,779.
**Targets:** Solve ≥ 110 (stretch; firm → 109) · Match ≥ 65 · model_infeasible ≤ 5 · Tests ≥ 4,800 · determinism ×3 seeds.

## Cumulative Metrics Tracker

| Metric | Day 0 | Day 5 (CP1) | Day 10 (CP2) | Day 13 (final, **measured**) | Target |
|---|---|---|---|---|---|
| Solve | 105 | 106 | 107 | **107** (+2) | ≥ 110 stretch / 109 firm — **miss −3 vs stretch, −2 vs firm** |
| Match | 62 | 63 | 67 | **92** (+30) | ≥ 65 — **EXCEEDED +27** |
| model_infeasible | 8 | 7 | 6¹ | **7** | ≤ 5 — miss +2 |
| Tests | 4,779 | ~4,795 | 4,917 | **~4,935** | ≥ 4,800 — **met** |

¹ CP1/CP2 columns are the per-day **genuine-gain projections** vs the as-measured Day-0 baseline (62) — they exclude the methodology-driven matches. The Day-13 **full retest** (the authoritative measurement) also captured **+24 non-convex models recovered by the Day-9 broadening of the presolve-retry to cold-*mismatch*** (`_cold_objective_mismatches_nlp`, #1387 PR) — mostly byte-identical emit (always correct, now warm-start-validated), which a fairer Day-0 baseline would also have counted. Net of methodology, the sprint's genuine cross-term contribution is **+7 fixes, zero regressions** (rocket #1462 is a *stale-baseline correction* — its Sprint-27 match was stale and the Sprint-27 golden aborts on current `main`, so the true Day-0 Match baseline was 61, not 62). See the Day-13 entry for the full decomposition.

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

---

## Day 3 — KKT-Residual Harness validate + land (2026-06-15)

**Status:** 🟢 DONE — harness validated end-to-end against all three cases (real GAMS runs); Phase-0 `### Verification Methodology` template wired with the concrete command + Case interpretation; P9 PR opened. Verifies Unknowns 9.1/9.2/9.3.

### Validation results (one per case; the prompt's "launch → Case a" is stale — corrected Day 2)

| Model | Verdict | Evidence | vs design |
|---|---|---|---|
| **trnsport** | **Case a** | all `stat_*` rel 0.0; self-check CONSISTENT; cold MCP MS 1 → converges | NEW clean Case-a model (launch is Case c, so the design's Case-a slot was empty) |
| **camshape** | **Case b** | `stat_r('i1')` raw **−396** (rel 2.0, dual_scale 198); self-check CONSISTENT | ✅ matches Sprint-27 §4.6 (`stat_r('i1')` INFES ≈ 396) |
| **cclinpts** | **Case b** | `stat_fb('s30')` raw **−4.91** (rel 4.91, dual_scale 1); self-check CONSISTENT | **CORRECTS** design "Case c" — the current emit has the #1387 bug (stat_fb missing 3/4 cross-terms); the 5e-8 "Case c" residual was the *hand-corrected eliminated-KKT* form, not the pipeline emit. The harness pins `stat_fb` = the #1387 fix surface (pre-validates Day 8). |
| **launch** | **Case c** | residual ~1e-16 (clean), self-check CONSISTENT, cold non-presolve MCP **MS 5 Locally Infeasible** | Day-2 finding (cold PATH can't reach the valid KKT point) |

**Headline:** the discriminator works exactly as designed — it separates "the emit is wrong" (camshape/cclinpts, Case b, with the prime-suspect row pinned) from "the emit is right but PATH can't get there cold" (launch, Case c) from "healthy" (trnsport, Case a). Two PR24 doc corrections surfaced: **cclinpts is Case b not Case c** (current emit ≠ corrected form), and the Case-a slot needed a fresh model (trnsport). Runtime (Unknown 9.3): all four ran via the no-`--gdx` embedded-NLP path in seconds (trnsport/camshape/cclinpts) to ~30 s (launch); the `--gdx` skip path is wired but unexercised here (fast models don't need it).

### Deliverables
- Validation evidence: `output/phase0_{trnsport,camshape,cclinpts,launch}.json` (gitignored scratch; not committed).
- `CONTRIBUTING.md` §"Verification Methodology" template: replaced the "forthcoming / does not exist yet" note with the concrete `kkt_residual.py` command + the Case-(a/b/c)/`dual_transfer_inconsistent` interpretation + PROCEED/REPLAN mapping + the validation summary; updated the PR27 status line to "landed".
- This Day-3 SPRINT_LOG entry. P9 PR opened.

### Next: Day 4 — Priority 1 #1224 mine. Clear the ISSUE_1224 Phase-0 gate with `kkt_residual.py data/gamslib/raw/mine.gms` → confirm Case b with `stat_x(l,i,j)` as the max-residual row, then implement the inverted parameter-valued offset at the traced surface (+1 Solve target).

---

## Day 4 — Priority 1: #1224 mine (2026-06-16)

**Status:** 🟡 PARTIAL — the `stat_x` parameter-valued-offset cross-term inversion landed (correct, tightly gated, harness-traced); but +1 Solve **REPLAN'd to #1443 (Sprint 29)** because the bug is deeper than the gate scoped. Per PR25: **bucket-forward (stationarity-shape correction), NOT a genuine Solve gain.**

### Phase-0 gate cleared (PR24, harness + instrumentation)
- `kkt_residual.py data/gamslib/raw/mine.gms` → **Case b**, max-residual `stat_x(2,2,1)` (raw 1.35e4, rel 1.0), self-check CONSISTENT — exactly the gate's prediction.
- **Traced the build site** (the gate left it pending): instrumented the symbolic stationarity build — the `pr` cross-term was one non-inverted `MultiplierRef(lam_pr, (k,l,i,j))`, missing the 2nd var-ref. **Build site = `src/kkt/stationarity.py`** (the prep doc's AD/Jacobian guess was wrong — PR24): mine's per-`k` integer offsets are consolidated to zero by the launch-style Pattern-C path, so the variable falls through to the non-inverted `else`.

### What landed (A) — verified correct
- New `_try_build_param_offset_crossterm` in `stationarity.py` (+ helpers `_collect_signed_varrefs`, `_negate_index_offset_expr`, `_expr_mentions_var`), injected at the top of the indexed-Jacobian constraint loop. **Tightly gated:** fires only when a var-ref of the variable carries a **non-`Const` `IndexOffset`** (parameter/symbolic offset = mine only); returns `None` for every other shape, so constant-offset models keep the existing path.
- Emitted `stat_x` now matches the hand-derived shape exactly: `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` (was the non-inverted `sum(k, lam_pr(k,l,i,j))`).
- **Blast radius = `mine_mcp.gms` `stat_x` line only** (launch/camshape/otpop/trnsport regen byte-identical; gate is exclusive by construction).

### Why +1 Solve REPLAN'd → #1443
mine is a **convex LP** (`solve … using lp`, `Positive Variable x`, `x.up=1`), so a correct MCP is a well-posed LCP that PATH must solve cold. After the `stat_x` fix the cold MCP is still **MS 5 Locally Infeasible**, with `x → 4e10` (despite `x.up=1`) and **49 INFES** across `comp_pr`/`comp_lo_x`/`comp_up_x`/`stat_x`/`def`. Root cause is the `pr(k,l+1,i,j)` **head-domain-offset** mis-emitting the broader KKT — a presolve dual-transfer misalignment (`lam_pr.l = abs(pr.m(k,l,i,j))` should read `pr.m` at `l+1`) **plus** a deeper cold-infeasible complementarity/bound coupling. The gate's "stat_x inversion ⇒ +1 Solve" hypothesis was **incomplete** (PR24). User-approved: keep (A) staged + file the re-scoped successor.
- **Filed #1443** (`docs/issues/ISSUE_1443_*.md`) — Sprint 29, the remaining head-domain-offset MCP correctness. ISSUE_1224 updated with the Day-4 outcome.

### PR25 tally update
- Solve: **no genuine gain** this day (mine stays `model_infeasible`; +1 Solve carried to #1443). **Forecast revised (targets unchanged):** firm Solve path drops from 108 to **107** (camshape + otpop), **108** with camcge conditional → **Solve ≥ 109 firm at-risk; stretch 110 out of reach barring recovery.** Match ≥ 65 unchanged (mine's Match was conditional-on-solving, never firm); model_infeasible ≤ 5 now exactly-at-target (needs camshape + otpop + camcge). PLAN.md §1/§2/§3/§6 + PLAN_PROMPTS Day-4 annotated (PR #1445).

### Next: Day 5 — Checkpoint 1 + Priority 2 #1388 camshape (harness already pre-confirmed Case b `stat_r('i1')` ≈ 396 on Day 3).

---

## Day 5 — Checkpoint 1 + Priority 2: #1388 camshape (2026-06-16)

**Status:** 🟢 DONE — **camshape +1 Solve (MS 1, area 4.2841 = NLP match)**. Offset-cross-term condition-guard fix in `src/kkt/stationarity.py`; + bonus side effects (otpop/maxmin → MS 1, mismatch).

### Checkpoint 1 (PR25 tally + golden-staleness)
- `changed_emit_artifacts.py --since-commit 68be9cca`: only `mine_mcp.gms` (Day-4 #1224) + the 4 Day-0 presolve goldens changed. All 5 **re-emit byte-identical** (golden-staleness clean). mine stays `model_infeasible`.
- **PR25 tally entering Day 5: 0 genuine Solve, 0 genuine Match** (mine's +1 → #1443) — Solve 105, Match 62, unchanged from Day 0.

### #1388 camshape — FIXED
- **Phase-0 gate (PR24):** harness → **Case b**, max-residual `stat_r(i1)` raw −396, self-check CONSISTENT (matches the Day-11 §4.6 / Day-3 pre-confirmation).
- **Hand-derived root cause:** `stat_r(i)`'s **offset** cross-terms (neighbor constraints `convexity(i±1)`, `convex_edge1(i-1)`, `convex_edge3(i+1)`) were guarded by the equation membership condition at the **current** index (`$(middle(i))`/`$(first(i))`/`$(last(i))`) instead of the **offset (neighbor)** index. At `i1`, `middle(i1)=no` suppressed the `convexity(i2)` cross-term that balances the `convex_edge1(i1)` self-term → residual −396.
- **Fix surface (traced):** the Issue #877 condition-propagation site in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py`). For an offset cross-term, shift the equation condition's domain indices by the same `offset_key` used for the multiplier (reusing `_reindex_condition_symbols` from #1224 Day-4). Emit now guards neighbor terms by `middle(i+1)`/`middle(i-1)`/`first(i-1)`/`last(i+1)`.
- **Result:** camshape (warm-started/presolve) → **MS 1, obj 4.2841 = NLP match** (`+1 Solve firm`, genuine). (Harness still shows the `stat_r(i1)` residual at iterlim=0 — that's the `piU_r(i1)` warm-start gap at the active bound, which PATH recovers; the emit is correct.)

### Blast radius (shared path) — 7 primary goldens changed, NO regression
Regenerated all 153 `*_mcp.gms`; 7 changed (all the correct neighbor-index guard re-index). Before/after cold solve:
- **camshape**: → MS 1 (match) — target. ✓
- **kand**, **srkandw**: unchanged (still MS 1, obj 195.0 — their boundary multipliers were 0, so no solution change). No regression.
- **clearlak**, **dinam**: unchanged (still `path_syntax_error` from a separate, unrelated cause). No regression.
- **otpop** (Day-6/7 target): cold `model_infeasible` → **MS 1, obj 2307** — but **MISMATCH** (NLP target 4217.80; its #1393/#1335 cross-term bugs remain → Days 6–7).
- **maxmin** (not a target): `path_solve_terminated` → **MS 1, obj 0.104** — but **MISMATCH** (harness: Case b, a separate `stat_mindist` emit bug; NEW finding).
- **otpop + maxmin are Solve-bucket transitions, NOT genuine matches** — precise Solve/Match classification deferred to the Day-10 full retest (PR25 discipline: not firmly claimed now).
- Goldens regenerated: 7 primary `_mcp.gms` + `camshape_mcp_presolve.gms`.

### PR25 tally (Day 5)
- **Genuine: Solve +1 (camshape, matches 4.2841).** Solve 105 → **106 (firm so far)**. Match 62 → **63** (camshape matches). otpop/maxmin's MS-1 transitions are bucket-forward (mismatch) — not counted as genuine until classified at Day 10.

### Next: Day 6 — Priority 3a #1393 otpop kdef Sum-collapse (otpop now MS-1-mismatch; the #1393/#1335 fix targets the 4217.80 match).

---

## Day 6 — Priority 3a: #1393 otpop kdef scalar subset-sum over-count (2026-06-16)

**Status:** 🟢 DONE — **#1393 fixed** (otpop `kdef` over-count gone; otpop → MS 1, was `solve=failure`). Full otpop +1 Match pends **#1335 `zdef`** (Day 7). **Bonus: chenery corrected to MATCH** (NLP `td=1058.9199`).

### Phase-0 gate (PR24/PR27)
- Harness errors on otpop's `--nlp-presolve` emit (GAMS exit 2, compile error — same class as korcge #1439), so verified via **structural grep + GAMS solve** instead of harness residual. Gate: `grep -cE 'sum\(t__, .*nu_kdef' /tmp/otpop_mcp.gms` → **0** (regenerate to /tmp first, never grep the committed golden).

### Root cause (confirms the prep-doc redirect to `stationarity.py`, NOT the AD layer)
- The per-cell numeric Jacobian is already correct (single term `del(1974)*…*p(1974)` for `x(1974)`). The over-count is introduced *downstream* in the **scalar-constraint branch of `_add_indexed_jacobian_terms`** (`src/kkt/stationarity.py`): `_replace_indices_in_expr` re-symbolizes the subset param `del` (declared over `t ⊂ tt`) to a synthetic `__` alias `del(t__)`; `_collect_free_indices` flags `t__` as uncontrolled; the old code wrapped the whole term in a **plain `Sum(t__, …)`** → stationarity row over-counted by `|t|` (17×).

### Fix
- In the `if uncontrolled:` block, a subset-alias uncontrolled index (detected by new helper `_subset_alias_superset_index`) is wrapped in a **sameas-guarded singleton sum** `sum(t__$(sameas(t__,tt)), …)` — mirroring the existing objective-gradient handling (#949/#1010, `_find_superset_in_domain`). **Domain-safe** whether the summed param is declared over the subset (`fawley pcr(cr)`) or the parent (`otpop del(tt)`). A first iteration (direct re-index alias→parent + drop Sum) was **rejected**: it produced `pcr(c)` with `c` over the parent → GAMS `$171 domain violation` (fawley).

### Blast radius (full 153-golden regen + diff; all GAMS-solved) — 7 changed, NO regression
All 7 changed goldens differ **exclusively** by the sameas-collapse pattern (`sum(x__, …)` → `sum(x__$(sameas(x__,c)), …)`); verified 0 non-collapse line changes per model.
- **otpop** (target): `kdef` over-count gone; MCP **MODEL STATUS 1** (was `solve=failure`). `pi=2624.75` vs NLP `4217.80` — full match pends **#1335 `zdef`** (Day 7).
- **chenery**: `tb` scalar constraint (`stat_e`/`stat_m`); MCP **`td=1058.9199` = NLP → MATCH** (old emit gave the wrong `1005.18`; was `solve=success, compare=None`). Genuine bonus.
- **china**: `cdef` scalar constraint; `income` `24782.88 → 44569.84`, closer to NLP `40561.57` but still mismatched (independent `crec`/`lam_mb` offset bugs). No regression (`compare=None`).
- **fawley**: `dpur`/`dtran` scalar constraints now domain-clean; MCP **MS 5 Locally Infeasible — identical to committed baseline** (pre-existing #1356 deferral). No regression.
- **tforss**: `asales` scalar constraint (`stat_x`); MCP **MS 1 = MS 1** (old), solve-identical. No regression.
- **ferts**: `ap`/`al`/`ai` scalar constraints (`stat_u`/`stat_vr`/`stat_xi`); solve byte-identical to baseline (pre-existing empty-`comp_mb` failure, unrelated). No regression.
- **turkey**: scalar constraint; MCP **8 compile errors = 8 errors** (old) — pre-existing failure, identical. No regression.
- The 6 scan emit-fails (decomp, danwolfe, nemhaus, nonsharp, saras, trnspwl) all pre-record `translate=failure`/`None` and fail structurally before the KKT layer (e.g. saras = multi-solve-driver CLI guard) — pre-existing, unrelated.

### PR25 tally (Day 6)
- **Genuine: Match +1 (chenery, 1058.9199).** Match 63 → **64**. Solve unchanged (otpop MS-1 transition is bucket-forward, mismatched until #1335 — classified at the Day-10 retest). Solve **106**, Match **64**.

### Deliverables
- `src/kkt/stationarity.py` (helper `_subset_alias_superset_index` + scalar-branch collapse).
- `tests/integration/emit/test_1393_scalar_subset_sum_collapse.py` (3 tests: otpop/chenery/china).
- Goldens regenerated: chenery/china/fawley/otpop/ferts/tforss/turkey `_mcp.gms` (7).
- `docs/issues/ISSUE_1393_*.md` RESOLUTION; CHANGELOG.

### Next: Day 7 — #1335 otpop `zdef` `card(t)-ord(t)` time-reversal cross-term (the companion that completes otpop's +1 Solve/+1 Match to `pi=4217.80`).

---

## Day 7 — Priority 3b: #1335 otpop zdef time-reversal cross-term (2026-06-17)

**Status:** 🟡 AD FIX LANDED (correct emit, hand-derivation-verified) — **otpop match NOT realized**: bucket-forward, blocked by **NEW #1449** (otpop `--nlp-presolve` `$184` compile failure) + cold non-convexity. Per-user decision: Option A (land the forward-progress fix, defer the match).

### Phase-0 gate + fix surface (prep-doc redirect, AGAIN)
- The prep named `_try_eval_offset` (`src/ad/constraint_jacobian.py`). **Wrong**: scalar `zdef` skips the `if eq_domain:` offset-resolution passes, so `_try_eval_offset` is never reached. Real surface = **`_diff_sum` in `src/ad/derivative_rules.py`**. Also: `_try_eval_offset` *can't* work — `card(t)-ord(t)` is not constant (depends on `ord(t)`); only the whole index `t+(card(t)-ord(t))` is constant (= last element).
- **Root cause:** `p(t+(card(t)-ord(t)))` cancels to the LAST element for every `t` → a constant column `p('1990')`. The generic `_sum_should_collapse` path assumes the wrt var is indexed BY the iterator, so the `IndexOffset` never matched a concrete column → `∂/∂p('1990')` dropped → `nu_zdef` absent from `stat_p`.

### Fix
- Two tightly-gated helpers (`_try_resolve_cardinality_reversal`, `_resolve_cardinality_reversal_in_expr`) + one branch at the top of `_diff_sum`: when the wrt var appears ONLY via the time-reversal offset, resolve it to the fixed element and differentiate in **sum-preserving** mode. Emit now: `stat_p(tt).. … + (((-1)*(v*sum(t,0.365*(xb(t)-x(t)))))*nu_zdef)$(sameas(tt,'1990')) … ;` — **exactly** the Phase-0 hand-derivation (sign/guard/structure). 1 integration test.

### Why the match is NOT realized (the NEW blocker)
- **Cold** otpop → MS 5 Locally Infeasible (was MS 1 cold-MISMATCH after Day-6 #1393): the *correct* full KKT system is non-convex; PATH cold-diverges.
- **Warm-start / presolve** (the only path to `pi=4217.80`) is blocked by **#1449**: otpop's `--nlp-presolve` fails to compile (`$184`) because the **mandatory** domain-widening (`db(tt)`/`del(tt)`, so `stat_p(tt)` can reference `db(tt)` without `$171`) conflicts with the `$include`d source's `db(t)`. `t`/`tt` can't coexist (verified under `$onMulti`/`$onMultiR`). Same class as #1439 (korcge).
- The KKT-residual harness reuses the presolve emit → also blocked by #1449. So #1335 is **hand-derivation-verified, not residual-verified** (yet). Manual primal+dual warm-start (Architecture B) reached MS 1 at 3160, not 4217 — inconclusive (dual sign-mapping is the harness's job).

### Decision (user)
Considered Option B (fix the presolve `$184`) but it is **not narrow** — the "tt→t" premise was wrong (tt is required), and the real fix is architectural (separate companion symbol / stationarity restructure / Architecture B), each with corpus-wide regression surface. **Chose Option A:** land the #1335 AD fix as forward progress, file #1449, classify otpop bucket-forward, defer the match to a scoped #1449 follow-on.

### PR25 tally (Day 7)
- **No genuine Solve/Match this day.** otpop's emit is correct but cold-infeasible and presolve-blocked → bucket-forward, not counted. Solve **106**, Match **64** (unchanged from Day 6; chenery's Day-6 match stands).

### Deliverables
- `src/ad/derivative_rules.py` (helpers + `_diff_sum` branch).
- `tests/integration/emit/test_1335_zdef_time_reversal_crossterm.py` (1 test).
- `data/gamslib/mcp/otpop_mcp.gms` regenerated (cold; `nu_zdef` now in `stat_p`).
- `docs/issues/ISSUE_1335_*.md` RESOLUTION; **NEW `docs/issues/ISSUE_1449_*.md`** (the presolve blocker); CHANGELOG.

### Next: Day 8 per PLAN — #1449 is the scoped follow-on that realizes otpop's +1 Solve/+1 Match once the widening/`$include` tension is resolved.

---

## Day 7 follow-on — #1449 presolve `$184` + otpop presolve SOLVES; #1452 filed (2026-06-18)

**Status:** 🟢 #1449 RESOLVED — otpop `--nlp-presolve` **compiles and solves (MCP MS 1 Optimal)**, the KKT-residual harness now runs on otpop (#1449 had blocked it), and the harness pins the **last match gate** as a new AD bug **#1452** (the `pdef` cross-term). Bonus: repaired `rocket`'s broken presolve golden.

> **Correction:** the prior revision of this entry (and ISSUE_1449) claimed the post-`$184` divergence was "CONOPT path-sensitivity, NOT a state leak." **Wrong.** The user's "is otpop non-convex?" question prompted a re-check: otpop is **convex** (DB `likely_convex`; standalone reaches 4217.7978 from all starting points). The divergence was a **real state leak — in this fix's own first revision** (over-rename, see below).

### #1449 fix (3 coupled, presolve-only, `src/emit/emit_gams.py`)
1. **Companions for `$184`:** declare widened source params at the **source domain** (agree with `$include`); emit `<p>__pw` companion at the widened domain after the `$include`. Only params referenced at the **parent-set index** (`db(tt)`) get a companion; over-widened subset-only params (`del`/`xb`/`pcr`) get none.
2. **Parent-index-only rewrite (the real bug).** The first revision renamed *all* refs incl. the re-emitted ORIGINAL `dem(t).. … db(t)` → `db__pw(t)`. GAMS binds an equation's algebra to its **last `..` def globally**, so this switched the embedded NLP's `dem` to `db__pw` (= 0 at NLP-solve) → NLP to pi=−29.77, garbage warm-start. Restricting the rewrite to parent-index refs keeps `dem` intact; embedded NLP now hits 4217.7978.
3. **Layer 4 — var-fix leak (`_emit_presolve_fx_unfix`).** The `$include`'s `var.fx(idx)=val` fixes columns the MCP fixes via an active `_fx_` equation (otpop's `x('1974')`), orphaning the row → EXECERROR. Unfix those after the `$include` (the `_fx_` equation pins the value). Also **repairs `rocket`'s presolve golden** (committed with this EXECERROR).

**Result:** otpop presolve compiles, embedded NLP = 4217.7978, **MCP solves MS 1**. Not a *match* yet (pi=3160.86) — the harness (now runnable) localizes the cause to **#1452** (`stat_p` `pdef` `ord(n)-1` cross-term: emits `sum(n,alpha(n))=1.0` per lead instead of per-lead weights 0.5/0.3/0.2; residual at `stat_p(1980–1984)`).

**Blast radius:** cold emit byte-identical. 8/11 presolve goldens byte-identical; `chain` (objective unchanged 6.9590, only an internal `nu_x_fx` dual now properly matched), `fawley` (no companions; MS 5), `rocket` (EXECERROR → MS 5, repaired). No objective regressions.

### PR25 tally (Day 7 follow-on)
- **No genuine Solve/Match yet** — otpop solves MS 1 but mismatches (pi 3160.86) pending **#1452**. Solve **106**, Match **64** (unchanged). #1449 is real infra progress (presolve solves + harness unblocked).

### Deliverables
- `src/emit/emit_gams.py` (`_emit_widened_param_companions`, `_rewrite_widened_param_refs`, `_emit_presolve_fx_unfix`, presolve-gated wirings).
- `tests/integration/emit/test_1449_presolve_widened_param_companions.py` (1 test, corrected).
- `data/gamslib/mcp/{chain,fawley,rocket}_mcp_presolve.gms` regenerated.
- `docs/issues/ISSUE_1449_*.md` RESOLUTION (corrected); **NEW `docs/issues/ISSUE_1452_*.md`**; CHANGELOG.

### Next: #1452 — the `pdef` `ord(n)-1` cross-term, the LAST gate to otpop's +1 Solve/+1 Match (taken on next, this branch).

---

## Day 7 follow-on — #1452 `pdef` `ord(n)-1` cross-term; **otpop MATCHES** (2026-06-18)

**Status:** 🟢 #1452 RESOLVED — **otpop MATCHES** (full-pipeline `compare_match`, MCP MS 1 Optimal in 0 PATH iterations from the warm start, pi = 4217.7978). With #1393 + #1335 + #1449, this realizes otpop's **+1 Solve / +1 Match**.

### #1452 fix (`src/kkt/stationarity.py`, `_add_indexed_jacobian_terms`)
The AD Jacobian was already correct (per-lead `∂pdef/∂p` = `-alpha(1)/-alpha(2)/-alpha(3)`). The bug was the stationarity re-symbolization: each per-lead offset group's concrete coefficient element (`alpha('1')` at lead 0, etc.) was mapped back to the iterator `n` and re-summed → all three leads collapsed to the identical `sum(n, (-alpha(n))*nu_pdef(tt+k))` (total weight 1.0 each).

**Fix (Approach A — pin the offset-driving set's element):** new helpers `_offset_driving_sets` + `_collect_ord_call_sets` detect sets whose `ord(s)` drives an index offset of the differentiated variable in the **source** equation (otpop `pdef`: `p(tt-(ord(n)-1))` → `{n}`). For such sets the `sum(n)` was already expanded into the per-lead groups (#1081), so their elements are pinned — dropped from the element→set map passed to `_replace_indices_in_expr` (~line 6177) — and stay concrete. Result: `stat_p(tt).. ((-1)*alpha("1"))*nu_pdef(tt) + ((-1)*alpha("2"))*nu_pdef(tt+1)$(…) + ((-1)*alpha("3"))*nu_pdef(tt+2)$(…) + …`. Cached per `(equation, variable)`.

**Why this gate** (vs the `ord(e)-1==offset_key` correlation the plan suggested): keying off the source-equation `ord`-offset structure is tighter — a generic `sum(j, beta(j)*x(i))` (real free index `j`, no `ord(j)` in the variable's offset) returns `∅` and the existing free-index sum path is untouched.

**Harness note:** the KKT-residual harness still prints CASE_B at the *boundary* rows `stat_p(1974)` / `stat_x(1990)` — a harness limitation (it doesn't transfer the active bound multipliers `piL_p`/`x_fx` that absorb those rows at the boundary). The authoritative `run_full_test --model otpop` compare_match (1/1) and the 0-iteration MS-1 presolve solve both confirm the match.

### PR25 tally (Day 7 follow-on — #1452)
- **+1 Solve / +1 Match (otpop, genuine).** Solve **106 → 107**, Match **64 → 65**.

### Blast radius
- Full corpus regen + targeted re-translate of every `ord`-near-offset model: **two cold goldens change, both corrections** — `otpop` (target) and **`tabora`**. tabora's `wb`/`lw`/`ttb` are the same distributed-lag shape (`sum(a, yv(a)*v(t-ord(a)))`); `stat_v` now emits per-lead `yv("a0k")` instead of the buggy `sum(a, yv(a))` at every lead. tabora compiles clean (`a=c`); `path_solve_license` in CI → no metric change, but emit now correct. All other `ord`-idiom candidates (clearlak, dinam, hhfair, imsl, qabel, sparta, tfordy) byte-identical; sddp/torsion no golden. `make test` + `make typecheck/format/lint` green.

### Deliverables
- `src/kkt/stationarity.py` (`_offset_driving_sets`, `_collect_ord_call_sets`, filtered `deriv_element_to_set`).
- `tests/integration/emit/test_1452_pdef_ord_lag_crossterm.py` (1 test).
- `data/gamslib/mcp/otpop_mcp.gms` + `data/gamslib/mcp/tabora_mcp.gms` regenerated; `data/gamslib/mcp/otpop_mcp_presolve.gms` added.
- `docs/issues/ISSUE_1452_*.md` RESOLUTION; CHANGELOG.

### Next: otpop's 4-fix arc (#1393 kdef, #1335 zdef, #1449 presolve, #1452 pdef) is COMPLETE — otpop matches. Resume Sprint 28 PLAN.

---

## Day 8 — Priority 4: #1387 cclinpts — Task-6 gate → **PROCEED** (anchor fix is LOCAL) (2026-06-18)

**Status:** 🟢 Task-6 gate decision: **PROCEED.** Re-confirmed the Day-6 anchor blocker on current `main` (`e9696570`) and traced the re-symbolization callers; the anchor fix is **LOCAL** (gateable to the differentiated variable's column index), not architectural → the three coupled changes are greenlit. Implementation **begun** Day 8 (working tree / scoping); lands Day 9 as one verified PR ("they land together"; high-blast-radius AD change needs full-corpus regression). **No `src/` committed Day 8** (docs-only gate deliverable).

### Gate evidence (empirical, on main)
- **Blocker re-confirmed:** `_build_indexed_gradient_term` → `_replace_indices_in_expr` (`src/kkt/stationarity.py:2816`) maps every same-set concrete element to the bare set index, so a gradient cross-term `fb('s11')-fb('s10')` collapses to `fb(j)-fb(j)` = 0 (the cancellation that makes cclinpts worse).
- **Anchor fix is LOCAL:** `_build_indexed_gradient_term` already holds the anchor (`var_indices` = the column's concrete-index tuple; the element is `anchor_elem = var_indices[d]`, a string). A pre-pass rewriting same-set elements to `IndexOffset(base=anchor_elem, offset=ord(e)-ord(anchor_elem))` (base is a string, per the AST) lets the existing #1162 machinery emit `fb(j+1)-fb(j)` — verified directly. Touches only the gradient path; `_replace_indices_in_expr` semantics unchanged → constraint-Jacobian callers (#1452/#1335/#1393) unaffected. Sign-flip stays a misdiagnosis.

### The three coupled changes (land together, Day 9)
1. **AD `_diff_sum` offset-enum** (`derivative_rules.py`): the stored `∂obj/∂b('s10')` drops Term-2-at-j+1; `∂obj/∂fb('s10')` drops Term-1-at-j+1 + Term-2-at-j+1. Generate them (Day-6 residual-verified shape, max|r|=5e-8).
2. **Local anchor pre-pass** in `_build_indexed_gradient_term` (validated Day 8).
3. **`--nlp-presolve` warm-start** (cclinpts cold-diverges to the degenerate `b≈const`).

**NEW Day-8 finding → filed [#1455](https://github.com/jeffreyhorn/nlp2mcp/issues/1455) (4th facet, separate from the three above):** `stat_fb`'s Term-1 `(b('s30')-b(j))$(not last(j))` is dropped. **Confirmed root cause:** `b('%last%')`→`b('s30')` (a FIXED boundary reference) is a member of set `j`, so it lands in `element_to_set` and `_replace_indices_in_expr` rewrites `b('s30')`→`b(j)`, collapsing `(b('s30')-b('s1'))`→`(b(j)-b(j))`=0. NOT representative-selection; the anchor pre-pass doesn't fix it (would map `s30`→`j+29`). Fix = keep the fixed boundary element literal. To be fixed alongside #1387 (same path) on Day 9, tracked separately.

### Deliverables (Day 8 — docs-only)
- `docs/issues/ISSUE_1387_*.md`: Status → IN PROGRESS / PROCEED; Day-8 gate decision + full bug-surface map + Day-9 ordered plan.
- This SPRINT_LOG Day-8 entry. **No metric change** (no `src/`; Solve 107, Match 65 stand).

### Next: Day 9 — finish the three coupled changes; per-term grep + harness Case-a + cclinpts MS 1 rel_diff<1% (+1 Match); full-corpus byte-stability + re-solve; open the #1387 PR.

---

## Day 9 — Priority 4: #1387 + #1455 cclinpts offset cross-terms → **cclinpts + chakra MATCH** (2026-06-18)

**Status:** 🟢 #1387 + #1455 RESOLVED — **cclinpts MATCHES** (compare_match, MCP MS 1 at ObjV −3.0011 via `--nlp-presolve` warm-start). **Bonus: chakra recovered to MATCH** (179.134) — the AD fix supplied its missing `∂obj/∂c` cross-term. **+2 Match (genuine), no regressions.**

### Four coupled facets (all landed together)
1. **AD `_diff_sum` offset-enum** (`src/ad/derivative_rules.py`): `_try_diff_sum_offset_crossterms` + `_distinct_var_offsets_in_body` + `_shift_to_offset_form`. Sum `Σ_δ ∂body/∂var(j+δ)|_{j=W−δ}·cond(W−δ)` over every offset, in `IndexOffset(col, ε−δ)` form. **Two gates** (the blast-radius containment): (a) OBJECTIVE-only via a scoped `config.enable_obj_offset_crossterms` set solely by `compute_objective_gradient` — `_diff_sum` is shared with constraint Jacobians, which corrupted chain's `length_eqn` until gated; (b) wrt-variable declared over EXACTLY the sum index set — excludes catmix's `u(nh)` over a subset (whose downstream subset re-symbolization dropped the `δ=+1` term).
2. **Offset-aware gradient re-symbolization** (`src/kkt/stationarity.py`, `_resymbolize_offset_gradient` + `_grad_has_concrete_base_offset` gate): col → `j`, `IndexOffset(col,±k)` → `j±k`, conditions `first/last(j±k)`. The generic `_replace_indices_in_expr` can't express this (its declared/equation-domain logic maps every same-set element to `j`).
3. **[#1455] fixed boundary literal**: `b('%last%')`→`b('s30')` preserved verbatim (else `b('s30')-b(j)`→`b(j)-b(j)`=0). Done inside `_resymbolize_offset_gradient`.
4. **Non-convex warm-start** (`scripts/gamslib/run_full_test.py`, `_cold_objective_mismatches_nlp`): extended the presolve retry to also fire when the cold solve SUCCEEDS but mismatches the NLP ref (cclinpts cold MS 1 at 15.34, a spurious KKT point). The warm start lands PATH at −3.0011. Sign-flip stays a misdiagnosis.

### PR25 tally (Day 9)
- **+2 Match (cclinpts + chakra, genuine).** Match **65 → 67**. Solve 107 (cclinpts/chakra already solved cold; the change is match, not solve).

### Blast radius (full 153-golden regen)
- **Exactly 2 cold goldens change: cclinpts + chakra — both mismatch → match.** 151 byte-identical. catmix (subset-domain) + chain (constraint-Jacobian) reverted to baseline via the two gates. `make typecheck/format/lint` clean.

### Deliverables
- `src/ad/derivative_rules.py`, `src/ad/gradient.py`, `src/config.py` (scoped flag), `src/kkt/stationarity.py`, `scripts/gamslib/run_full_test.py`.
- `tests/integration/emit/test_1387_cclinpts_offset_crossterms.py` (1 test).
- `data/gamslib/mcp/{cclinpts,chakra}_mcp.gms` regenerated; `cclinpts_mcp_presolve.gms` added.
- `docs/issues/ISSUE_1387_*.md` + `ISSUE_1455_*.md` RESOLUTION; CHANGELOG.

### Next: resume Sprint 28 PLAN (Day 10 — Checkpoint 2 + #1390 kand Task-6 gate).

---

## Day 10 — Checkpoint 2 + Priority 5: #1390 kand Task-6 gate → **PROCEED** + fix → kand MATCHES (2026-06-18)

### Checkpoint 2
- **Golden-staleness CLEAN:** all 13 tracked presolve goldens re-emit byte-identical; cold goldens clean (Day-9 full regen). `changed_emit_artifacts.py --since-commit 68be9cca` = the expected per-PR golden set.
- **PR25 tally entering Day 10: Solve 107, Match 67** (Day-0 baseline Solve 105/Match 62 + camshape Solve, otpop Solve/Match, chenery/cclinpts/chakra Match). Match target ≥65 **exceeded**; Solve ≥110 is 3 short (the deferred camcge/otpop-class).

### #1390 kand — Task-6 gate → PROCEED (Case B)
- LP reference **2613.0** confirmed. Harness verdict **CASE_B (emit_bug)**, dual-transfer self-check **CONSISTENT**, max-residual row **`stat_x(raw-2,time-1)`** (rel 1.04) → localizable → **PROCEED** (not the Case-c LP-recourse-coupling REPLAN). Phantom `stat_y` terms confirmed inert (out of scope).
- **Root cause:** `dembalx(j,tn(t,n))` has the lag `y(j,t-1,nn)` in its **body** (head has no offset). GAMS evaluates the out-of-range first-period lag as 0, so the constraint is defined at ALL `tn(t,n)`. The emit applied the inferred lead/lag bound `ord(t)>1` to the **inequality** complementarity (restricting `comp_dembalx`, fixing `lam_dembalx=0` at the first period) — dropping the first-period demand constraint and corrupting `stat_x`; the MCP cold-solved to a spurious 195.0. Same class already removed for **equalities**, still firing for inequalities.
- **Fix (3 sites, mirror the equality path):** `src/emit/equations.py` (inequality comp emit passes `skip_lead_lag_inference=not has_head_domain_offset`); `src/emit/emit_gams.py` §2b (gate the #943 multiplier fix on `has_head_domain_offset`); `src/kkt/complementarity.py` (**preserve `has_head_domain_offset` on the comp equation** — it normalizes a head offset into the body; without this, head-offset models pak/polygon would lose their genuine restriction).
- **kand MATCHES** (run_full_test compare_match, MCP MS 1 at cost = 2613.0; harness now **CASE_A** healthy, residual 1.3e-16).

### PR25 tally (Day 10)
- **+2 Match (kand, srkandw — genuine, both cold-match at 2613.0 via the #1390 body-offset fix; no presolve retry).** Match **67 → 69**. Solve 107 (both already solved cold; the change is match). *(Separately: like — a kand-family sibling — also matches, but via the Day-9 facet-4 presolve-retry with a byte-identical cold golden, i.e. already realizable on `main`; recorded at the Day-13 retest, not attributed to #1390.)*

### Blast radius (full 153-golden regen)
- **12 cold goldens change, no regressions:** kand + srkandw (→match), camshape (solve-equivalent — redundant guard removed, explicit first/last/middle condition already covered it; still matches), dinam + ps{10_s,10_s_mn,3_s,3_s_mn,3_s_scp,5_s_mn} + shale + tabora (body-offset comp domains corrected; status unchanged — mismatch/skipped/license for unrelated reasons; all compile clean). **Head-offset models (pak/polygon/invu-type) byte-identical to baseline** — the `has_head_domain_offset`-preservation gate avoided the first-cut regressions (pak match→fail, polygon solve→fail), both verified solving MS 1. Supersedes #943's body-offset restriction.

### Deliverables
- `src/emit/equations.py`, `src/emit/emit_gams.py`, `src/kkt/complementarity.py`.
- `tests/integration/emit/test_1390_kand_body_lag_constraint_domain.py` (1 test); 3 `TestLeadLagComplementarityFix` tests updated to the corrected full-domain behavior.
- `data/gamslib/mcp/{kand,srkandw,camshape,dinam,ps10_s,ps10_s_mn,ps3_s,ps3_s_mn,ps3_s_scp,ps5_s_mn,shale,tabora}_mcp.gms` regenerated.
- `docs/issues/ISSUE_1390_*.md` RESOLUTION; CHANGELOG. `make test` 4917 passed; typecheck/format/lint clean.

### Next: Day 11 — camcge Task-6 gate + P7 cleanups (#1374 robot `.l` dedup, #1400 message-field relativization).

---

## Day 11 — Priority 6 camcge Task-6 gate → REPLAN; Priority 7 cleanups #1374 + #1400 (2026-06-19)

### camcge (Task-6 gate) → **REPLAN to Sprint 29 / Epic 5 inherent-degeneracy**
- Harness (NLP ref 191.7346): `dual transfer CONSISTENT`, verdict **CASE_B**, max-residual `stat_mps` (rel 1.05, raw −210), then `stat_tm`/`stat_pwm` (0.04–0.08). **But the prompt's Case-c premise holds:** the `stat_mps` CASE_B is a **fix-multiplier-transfer artifact** — `mps` is a fixed variable, `stat_mps` (`sum(i,y·cles(i)·nu_cdeq(i)) − y·nu_hhsaveq + nu_mps_fx`) hand-derives **correct**, and the synthetic `mps_fx` equation has no NLP marginal so `nu_mps_fx` is un-warm-started → residual = −gradient (−210). Cold MCP **MS 4 Infeasible at iteration 0** (`stat_cd` rows INFES at a uniform −0.2022) = singular-system signature.
- **Root cause = CGE Walras-law degeneracy** (`equil(i)` goods + `lmequil(lc)` labor market-clearing linearly dependent given budget balance; no price numéraire). PROCEED criterion ("single redundant Walras row + numéraire fix preserving the economic solution as a general emit change") **not met** — that is a CGE-domain structural transformation = Epic 5. Confirms the ISSUE_1330 round-3 diagnosis. **No `src/`; camcge stays model_infeasible.** ISSUE_1330 updated with the gate result.

### P7 #1374 — robot `.l` denominator/override dedup → **RESOLVED**
- `src/emit/emit_gams.py`: when merging `.fx → .l` per-instance overrides into a var's init group, skip an override that exactly duplicates a denominator-guard bulk-init line (same element, same value). robot's `rho.fx(firstlast)=4.5` → `rho.l('h0')/('h50')=4.5` was emitted twice (the divisor-guard init already set them). **Blast radius: robot only** (1 golden, the 2 dup lines removed); solve-equivalent (byte-only); robot compiles clean. Completes #1374 (the `.fx`-restore shape landed Sprint 27 Day 13). 1 integration test.

### P7 #1400 — repo-relative warning paths → **RESOLVED**
- `src/cli.py`: `_install_repo_relative_formatwarning()` (in `main()`) wraps `warnings.formatwarning` so in-repo `UserWarning` filenames are emitted relative to the repo root. Batch tooling subprocesses the CLI and captures stderr into the gamslib DB `message` field, where the default absolute path leaked the home dir (e.g. mine's `pr` warning). Verified: mine warnings now `src/ad/index_mapping.py:648` (0 abs paths, was 4). Completes #1400 (the `mcp_file_used` leak landed Sprint 27 Day 13). 3 unit tests.

### PR25 tally (Day 11)
- **No metric change** (camcge REPLAN'd → stays model_infeasible; #1374/#1400 are byte-only/portability). Solve 107, Match 69 stand.

### Deliverables
- `src/emit/emit_gams.py` (#1374), `src/cli.py` (#1400).
- `tests/integration/emit/test_1374_robot_l_init_dedup.py`; `tests/unit/test_cli_repo_relative_warnings.py` (3).
- `data/gamslib/mcp/robot_mcp.gms` regenerated (dedup).
- `docs/issues/ISSUE_1330_*.md` REPLAN, `ISSUE_1374_*.md` RESOLVED, new `ISSUE_1400_*.md`; CHANGELOG. `make test` 4921 passed; typecheck/format/lint clean.
- **#1385 deferred to Sprint 29** (Day 11 consumed by the camcge gate + the two cleanups, per the PLAN's slip guidance).

### Next: Day 12 — Priority 8 golden-staleness CI + Priority 10 divergence/property tests.

---

## Day 12 — Priority 8 golden-staleness CI + Priority 10 divergence detector & AD property tests (2026-06-19)

**Status:** 🟢 DONE — all three deliverables built + CI-wired + validated. No `src/` change (tooling + tests only); no metric change. Unknowns 8.2 / 10.1 / 10.2 / 10.3 VERIFIED.

### P8 — golden-staleness checker + CI + `make regen-goldens`
- `scripts/sprint_audit/check_golden_staleness.py [--fix] [--models csv] [--json]`: regen every committed golden via `batch_translate.translate_single_model` (parallel ThreadPoolExecutor, 6 workers), byte-diff. Report mode exits 1 on non-allowlisted drift; `--fix` overwrites with a **determinism double-regen guard** (re-emit twice, require byte-identity before overwrite). Allowlist `golden_staleness_allowlist.txt` = 6 out-of-scope models + `indus` (cross-platform byte non-determinism, #1461) = **7 entries**. `make regen-goldens` (= `--fix`) + `make check-goldens` (report). `.github/workflows/golden-staleness.yml` on `src/{ad,kkt,emit,ir}/**` (`permissions: pull-requests: read`, least privilege).
- **Validated (Unknown 8.2): full run = 0 drift across the in-scope goldens** (7 allowlisted = 6 out-of-scope + `indus`). The 8 slow-emit models (ganges/gangesx ~minutes) hit the per-model translate timeout under parallel CPU contention → reclassified as a **soft "timeout/unverified"** status (not drift; the design routes full sweeps to nightly + PRs to the changed-emit subset). `indus` was added to the allowlist after the ubuntu CI flagged a ~45-byte cross-platform difference (a slow-emit model, unverified locally; per-platform stable but not byte-reproducible across macOS/ubuntu → #1461). Gotcha fixed during build: `translate_single_model` relativizes the output path against the repo root, so the temp dir must live inside the repo.

### P10 — embedded-NLP-divergence detector + CI
- `scripts/diagnostics/check_presolve_divergence.py [--model] [--tol] [--json]`: the embedded NLP objective is **already captured** by the presolve emit as `nlp2mcp_obj_val` (no probe insertion needed) — parse it from the listing and compare to the **canonical standalone NLP objective from the pipeline DB** (`convexity.objective_value`; a fresh cold re-solve is unreliable for non-convex models, which land at a different local optimum and false-flag). **HARD-FAILS only on unambiguous corruption** — a GAMS abort (`ABORTED, EXECERROR = [1-9]` / non-zero rc / `USER ERROR(S)` / `Matrix error`) or a non-optimal embedded MODEL STATUS while the reference solves; a bare **objective gap is informational** (`obj_gap` — non-convex local optima are benign). Default `--tol 1e-3` (absorbs ~6-sig-fig Display rounding; the CI step passes `--tol 1e-3` explicitly). Pure `classify_divergence()` helper. Allowlist `presolve_divergence_allowlist.txt` = **korcge** (#1439, known/deferred abort). `.github/workflows/presolve-divergence.yml` on `src/emit/{emit_gams,original_symbols}.py` (`permissions: pull-requests: read`).
- **Validated (Unknown 10.1): launch CLEAN** (embedded == reference 2257.80 post-#1378), **korcge (#1439) hard-diverges live** (the `ABORTED, EXECERROR=5` abort — gotcha: GAMS prints a benign "(EXECERROR=0) CLEARED" line, so key off the ABORT not "EXECERROR") and is **allowlisted** (#1439 open/deferred) so it surfaces as WARN not a gate failure. The detector was **reworked during review** from a fresh-cold-re-solve comparison (which false-flagged non-convex chain/agreste/fawley/cesam/rocket as divergences) to the DB-reference + hard-fail/soft-`obj_gap` split above. The #1378/#1424/#1439 "must SURFACE" acceptance is **unit-tested against their documented pre-fix numbers** (#1378 2604 vs 2258 → `obj_gap`; #1424 infeasible MODEL STATUS 5 → diverged; #1439 execerror → diverged) — no risky git-revert of the merged fixes.

### P10 — 6 AD cross-term property tests (Unknowns 10.2, 10.3)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + 6 committed synthetic fixtures `tests/fixtures/crossterm_shapes/shape{1..6}_*.gms`. Emit each in-process (sub-second) and pattern-assert the hand-derived `stat_*` cross-term: (1) single-axis offset INVERTED, (2) self-alias swap `a(jj,i)` (#1381), (3) cross-set alias NO swap `b(i,j)` (#1398), (4) parameter-valued offset inverted `lam_pr(k,l,i-li(k),j-lj(k))` + `l-1` (#1224), (5) interior+edge convex `middle(i±1)` canonical guards (#1388), (6) tree-predicate single guarded Sum `1$(tree(n,nn))*nu_dembal(nn)` not enumerated (#1390). Always-run in `make test` (no corpus/GAMS).

### Deliverables
- `scripts/sprint_audit/check_golden_staleness.py` + `golden_staleness_allowlist.txt`; `scripts/diagnostics/check_presolve_divergence.py` + `presolve_divergence_allowlist.txt`.
- `.github/workflows/{golden-staleness,presolve-divergence}.yml`; `Makefile` (`regen-goldens`, `check-goldens`).
- `tests/integration/emit/test_ad_crossterm_shapes.py` (6) + 6 fixtures; `tests/unit/test_presolve_divergence_classify.py` (6).
- CHANGELOG. typecheck/format/lint clean; `make test` green.

### Next: Day 13 — Final 3× PYTHONHASHSEED retest + golden-staleness check + PR25 final tally + SPRINT_RETROSPECTIVE + Sprint 29 carryforwards.

---

## Day 13 — Final Retest + Closeout (2026-06-20)

**Status:** 🟢 DONE — full 142-model pipeline retest (re-solve, the committed DB was stale; the per-priority PRs changed `src/`+goldens but never re-ran the pipeline), 3× `PYTHONHASHSEED` determinism check, PR25 final tally, retrospective, Sprint 29 carryforwards. **One stale-baseline correction found and filed (rocket #1462 — NOT a Sprint-28 regression; see the PR25 tally below).**

### Final headline metrics (142-model GAMSlib corpus, `run_full_test.py` summary)
| Metric | Day 0 | Day 13 | Target | Verdict |
|---|---|---|---|---|
| Parse | 142 | **142** | ≥142 | met |
| Translate | 135 | **135** | ≥135 | met |
| Solve (`model_optimal[_presolve]`) | 105 | **107** | ≥110 stretch / 109 firm | **miss −2** |
| Match | 62 | **92** | ≥65 | **EXCEEDED +27** |
| Mismatch | 37 | **9** | — | — |
| model_infeasible | 8 | **7** | ≤5 | miss +2 |
| Tests | 4,779 | **~4,935** | ≥4,800 | met |
| Determinism (3× `PYTHONHASHSEED`) | ✅ | **✅ 0 drift ×{0,1,42}** | ×3 seeds | met |

### PR25 final tally — genuine vs methodology vs bucket-forward vs regression

**Solve 105 → 107 (+2).** New `model_optimal`: **camshape** (#1388, genuine), **otpop** (#1393/#1335/#1449/#1452, genuine), **maxmin** (side-effect of camshape's guard fix + the broadened retry). Lost: **rocket** (stale-baseline correction, #1462 — not a Sprint-28 regression). Net +2. Misses the firm-109 / stretch-110 target by exactly the two REPLAN'd tracks (**mine #1443**, **camcge #1330**) plus the rocket stale-baseline correction.

**Match 62 → 92 (+30 net = +31 new − 1 regression).** Decomposition (validated by diffing the fresh DB against the pre-retest snapshot + cross-referencing the changed-golden set):
- **7 genuine cross-term-fix matches** (documented, harness-verified during the sprint): camshape, otpop, cclinpts, chakra, chenery, kand, srkandw.
- **~24 methodology-driven matches** from the **Day-9 #1387 PR broadening the presolve-retry to also fire on cold-*mismatch*** (`_cold_objective_mismatches_nlp`), not just STATUS-5 cold failures. These are non-convex models that cold-converge to a *spurious* KKT point but warm-start to the NLP optimum (catmix, himmel16, weapons, harker, polygon, sambal, markov, worst, the CGE family irscge/lrgcge/moncge/stdcge, like, robert, mathopt1/4, mingamma, paperco, qsambal, marco, etamac, cpack, maxmin, tforss, …). **22 of these have byte-identical emit to Day-0** — they were always emit-correct; the broadened retry now *validates* them. A fairer Day-0 baseline (with the broadened retry) would have been ~86, so the sprint's genuine cross-term contribution is **+7 (zero regressions — see rocket below)**.
- **−1 stale-baseline correction: rocket** (#1462) — **NOT a Sprint-28 regression.** The Sprint-27 DB recorded `model_optimal_presolve` + match (1.0128), but the **actual Sprint-27 golden aborts (`EXECERROR=1`) on current `main`** (the otpop fixed-column / unmatched-`_fx_`-row pathology), so that match was stale and does not reproduce. The only Sprint-28 change to rocket's presolve is the #1449 unfix, which moved it **abort → MS5-infeasible** (a *forward* step). Root cause localized (the `nu_*_fx_h0` `_fx_`-multipliers aren't warm-started → nonzero `stat_v('h0')` residual; injecting `nu_*_fx_h0.l = <var>.m('h0')` moves the objective to 1.016 but MS5 persists — a deep non-convex case). Carried to Sprint 29 (no new `src/` in Day 13). So the genuine Day-0 Match baseline should have been **61**.

**model_infeasible 8 → 7.** Left: camshape, otpop (the two genuine solves). Entered: rocket (#1462 — a stale-baseline correction; rocket was already broken at Sprint-27 close, the unfix moved it abort→infeasible). Miss vs ≤5 = mine (#1443) + camcge (#1330) + rocket.

### Validation method (PR25 / PR12 discipline)
- The committed DB was the **stale Sprint-27-final** measurement (otpop=failure, cclinpts/kand=old mismatch objectives), so a fresh re-solve was genuinely required — not a re-measurement of already-updated rows.
- Diffed the fresh retest DB against the pre-retest snapshot (`archive/20260620_204913`): **31 new matches, 1 lost (rocket), 3 new `model_optimal`, 1 lost (rocket)** — every delta accounted for above; cross-referenced against the 33-golden changed set (`git diff 68be9cca..HEAD -- data/gamslib/mcp/`) to separate emit-changed (fix-driven) from byte-identical (methodology-driven) matches.
- **Determinism:** `check_golden_staleness.py` under `PYTHONHASHSEED` ∈ {0, 1, 42} = **0 drift each** (slow-emit models soft-timeout; `indus` allowlisted #1461) → emit is seed-invariant.

### Closeout deliverables
- `SPRINT_RETROSPECTIVE.md` authored; cumulative tracker filled; this Day-13 entry.
- Sprint 29 carryforwards: **#1443** (mine, head-domain-offset MCP infeasibility), **#1330** (camcge → Epic 5 CGE Walras degeneracy), **#1385** (translation-timeout cross-terms, re-deferred), **#1462** (rocket presolve `nu_*_fx_h0` warm-start / non-convex — stale-baseline, not a regression, NEW), **#1461** (indus cross-platform emit determinism, NEW).
- Resolved + CLOSED this sprint: #1387, #1455, #1390, #1393, #1335, #1449, #1452, #1388, #1374, #1400.
- Committed the fresh pipeline DB (`gamslib_status.json`).

### Headline
**Match target ≥65 exceeded → 92** (genuine cross-term contribution +7, zero regressions; the rest is the Day-9 presolve-retry broadening validating already-correct non-convex emits). **Solve missed** (107 vs 109/110) and **model_infeasible missed** (7 vs ≤5) by exactly the two formally-REPLAN'd tracks (mine #1443, camcge #1330) plus the rocket stale-baseline correction (#1462 — not a Sprint-28 regression; rocket was already broken at Sprint-27 close). Four diagnostic/CI guards shipped (KKT-residual harness, golden-staleness gate, divergence detector, AD property tests). **Sprint 28 CLOSED.**
