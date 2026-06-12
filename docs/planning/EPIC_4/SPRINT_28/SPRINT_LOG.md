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

### Next: Day 1 — begin building the KKT-residual harness (Priority 9, front-loaded Days 1–3).
