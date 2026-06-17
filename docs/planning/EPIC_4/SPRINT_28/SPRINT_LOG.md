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
