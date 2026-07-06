# Sprint 30 — Reusable-Tooling Readiness Audit

**Task:** Sprint 30 Prep Task 8 (audit-only — read-only tool runs, zero `src/` diff)
**Date:** 2026-07-06
**Scope:** the Sprint-28/29 diagnostic/CI tools Sprint 30 reuses (`kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py` + `changed_emit_artifacts.py` + `run_full_test.py --resolve-changed`, and the AD property-test catalog), audited against the **new Sprint-30 model classes**: head-domain-offset multipliers (`lam_pr`/`nu_sb`, mine/robert P1), the widened-VARIABLE presolve emit (hhfair P3), the forcing-harness scaffold (P2/P8), and the offset-alias-successor cross-term shape (himmel16/polygon P5).
**Verdict:** **all tools are ready for Sprint 30 — the only gap is ONE *optional*, non-blocking ≤ 1 h harness extension** (a head-label warm-start for head-offset multipliers to make the harness's *per-row localization* trustworthy on base-normalized head-offset equations). The dual-transfer self-check itself is **CONSISTENT** on both robert and mine, and the standing mitigation (the cold-solve control experiment, proven by Task 3) already produces the correct diagnosis without it. Everything else: no extension needed.

> **Sprint-30 nuance vs the Sprint-29 "gap list = NONE".** Sprint 29's audit found the harness *fully* ready. Sprint 30's head-offset class surfaces a subtler point (the exact Task-8 "trust the tool's actual output, not the assumed one" lesson): the harness dual-transfer self-check reports **CONSISTENT** for the head-offset `nu_sb`/`lam_pr` multipliers — but for **base-normalized head-offset equations** (robert's `sb(r,tt)$(ord(tt) <= card(tt) - 1)`), the *same-index* warm-start (`nu_sb.l = sb.m`, NLP marginals stored at the **head** label) shifts the multiplier by one, so the harness's **top per-row residual is a transfer artifact**, not the operative bug (robert's top `stat_x(high,3)` rel 7.20 is the artifact; the real bug is the `stat_s` objective gradient — Task 3 §1.5). CONSISTENT ≠ "the top row is the bug." The mitigation is the cold-solve control experiment (Task 3), so this is a **methodology caveat + an optional extension, not a Day-0 blocker.**

---

## Tool 1 — `kkt_residual.py` (KKT-residual harness) — head-offset dual-transfer

**New classes to cover:** the head-domain-offset multipliers — `nu_sb` at the `tt+1` head (robert #1443/objgrad) and `lam_pr` at the `l+1` head × `li(k)`/`lj(k)` parameter offsets (mine #1443). Task 3 relies on the harness verdict being trustworthy; the risk (Unknown 1.4) is that the dual-transfer self-check mis-maps these synthetic multipliers.

**Audit — actual harness runs (this task, `data/gamslib/raw/{robert,mine}.gms`):**

| Model | Class | `dual transfer` self-check | Verdict | Top row |
|---|---|---|---|---|
| **robert** | head-offset `nu_sb` (base-normalized `sb(r,tt)`) | **CONSISTENT** (max comp infeas 0.00e+00, max equality residual 0.00e+00) | CASE_B — emit_bug | `stat_x(high,3)` rel **7.20** |
| **mine** | head-offset `lam_pr` at `l+1` × `li(k)`/`lj(k)` | **CONSISTENT** (max comp infeas 0.00e+00, max equality residual 0.00e+00) | CASE_B — emit_bug | `stat_x(4,1,1)` rel **1.33** |

**Readiness: ✅ READY (self-check) + ⚠️ one optional ≤ 1 h extension (per-row localization).**

- **The dual-transfer self-check is CONSISTENT on both** — the harness loads the head-offset `nu_sb`/`lam_pr` multipliers into the warm-start with **no mis-transfer and no false "inconsistent" flag** (the `--nlp-presolve` emit loads every multiplier class `nu_<eq>.l = eq.m` / `lam_<eq>.l = abs(eq.m)` as ordinary rows; the self-check validates them with no special-casing). So the residual the harness reads is numerically self-consistent, and the tool **runs** on the head-offset class without a Day-0 change.
- **The caveat is per-row *localization*, not the self-check.** For a **base-normalized head-offset equation** (robert's `sb(r,tt)$(ord(tt) <= card(tt) - 1)`, multiplier `nu_sb(r,tt)`), the NLP stores the marginal `sb.m` at the **head** label `(r,tt+1)`, so the harness's same-index warm-start `nu_sb.l(r,tt) = sb.m(r,tt)` is shifted by one → the per-row residual of `stat_x`/`stat_s` is corrupted, and the **top row is a transfer artifact** (robert `stat_x(high,3)` 7.20 is the artifact; Task 3's cold-solve control proved the operative bug is `stat_s`). For **mine** the top `stat_x(4,1,1)` 1.33 is closer to a real site (the landed `stat_x` cross-term is one of mine's three coupled sites), but the same shift applies.
- **Standing mitigation (no code): the cold-solve control experiment.** Task 3 localized robert correctly by patching `robert_mcp.gms` cold and reading the objective (6741.67 vs 11025.0), **not** by trusting the harness top row. For head-offset models, the Day-0 method is: read the harness dual-transfer verdict (CONSISTENT ⇒ warm-start valid) **and** corroborate the operative row with a cold-solve control patch. This is already the Task-3/Task-5 gate methodology.
- **Optional ≤ 1 h extension (Day-0, non-blocking):** teach the harness to warm-start head-offset multipliers at the **head** label for base-normalized head-offset equations (`nu_<eq>.l(idx) = <eq>.m(head(idx))`), so the per-row residual is trustworthy without the cold-solve control. Scope: a single index-map branch in the harness's dual-transfer warm-start for equations flagged as head-offset-normalized. **Not required** for the sprint (the cold-solve control is the proven method), so it is a nice-to-have, not a blocker.

---

## Tool 2 — `check_presolve_divergence.py` (embedded-NLP divergence detector)

**New classes to cover:** the **Class-B CGE cluster** (irscge/lrgcge/moncge/stdcge — the `stat_pz` coefficient discrepancy, P7) and the **cold-convex residue** (bearing/launch/mathopt3/robustlp + rocket, P2). The detector must **soft-classify** these (informational `obj_gap`), not hard-fail, or the Day-5/Day-10 checkpoints flood.

**Audit — the detector's classification logic (`classify_divergence`, read-only):**

- **HARD-FAILS (exit 1)** on unambiguous `$onMultiR` corruption, one of three triggers: (a) `execerror` — the embedded `$include` run **aborted** (korcge #1439); (b) the **embedded NLP is infeasible / non-optimal** (MODEL STATUS ∉ {1,2}) while the reference is optimal (camshape #1424); or (c) the **embedded presolve produced no objective value** (`emb_obj is None` — an unparseable/absent objective). Triggers (b) and (c) both require a canonical reference (else the model is `skipped`, never failed). It gates on the **embedded NLP**, never on the MCP.
- **SOFT signal** (`obj_gap`, reported but **not** failed): the embedded NLP *solves* but its objective differs from the canonical reference.

| Class | Embedded-NLP status | MCP status | Detector result | Hard-fail? |
|---|---|---|---|---|
| **Class-B CGE** (irscge/lrgcge/moncge/stdcge) | optimal (models already `model_optimal_presolve` + match) | `stat_pz` coefficient discrepancy (P7) | soft — the detector does **not** gate on the MCP; embedded NLP is optimal | **No** |
| **Cold-convex residue** (bearing/launch/mathopt3/robustlp) | optimal (already warm-match, residual ≤ 8e-6) | matches | no divergence / 0 obj-gap | **No** |
| **rocket** (#1462) | MS 2 (embedded solves) | MS 5 (intrinsic non-convergence) | informational `obj_gap` — detector gates on the embedded NLP, not the MS-5 MCP | **No** |

**Readiness: ✅ READY — no extension, no new allowlist entry.** Because the detector gates on the **embedded NLP** (which for every one of these classes solves optimally **and** yields a parseable objective) and never on the MCP, none of the three hard-fail triggers (abort / non-optimal-embedded / no-objective) fires — so the Class-B `stat_pz` MCP discrepancy and rocket's MS-5 MCP both soft-classify. The hard-fail triggers are unchanged from Sprint 29 (korcge #1439 allowlisted; camshape #1424 fixed). No Sprint-30 class introduces a new hard-fail.

---

## Tool 3 — `check_golden_staleness.py` + allowlists + `changed_emit_artifacts.py` + `run_full_test.py --resolve-changed`

**New classes to cover:** the Sprint-30 emit-touching work regenerates goldens — the **widened-VARIABLE presolve** emit (hhfair P3, a `*_mcp_presolve.gms` regen) and the **head-offset** emit (mine/robert P1, a `*_mcp.gms` regen). The staleness gate + the changed-golden diff must (a) not flap on the known out-of-scope models and (b) feed the right at-risk set into the Day-5/Day-10 checkpoint re-solve.

**Audit — allowlist currency + `--resolve-changed` coverage:**

- **Golden-staleness allowlist** (`scripts/sprint_audit/golden_staleness_allowlist.txt`): **7 entries, all still valid** — 3 multi-solve drivers (danwolfe, decomp, saras) + 3 discrete MIP/MINLP (nemhaus, nonsharp, trnspwl) + **indus** (cross-platform byte non-determinism, #1461). Unchanged from Sprint 29; no Sprint-30 model needs adding or removing.
- **Presolve-divergence allowlist** (`scripts/diagnostics/presolve_divergence_allowlist.txt`): **1 entry — korcge** (#1439).
- **Issue states:** **#1439 (korcge) OPEN** and **#1461 (indus) OPEN** — both allowlist entries still track live deferred bugs, so neither is removed.
- **`--resolve-changed` covers both Sprint-30 golden kinds.** `run_full_test.py` defines `_GOLDEN_SUFFIXES = ("_mcp_presolve.gms", "_mcp.gms")` (longest-first so `_mcp_presolve` wins), and `_changed_golden_model_ids(since_commit)` git-diffs `<SHA>..HEAD` for changed goldens of **either** suffix. So the changed-golden set surfaces **both** the widened-VARIABLE **presolve** regen (hhfair `_mcp_presolve.gms`) **and** the head-offset **cold** regen (mine/robert `_mcp.gms`) as at-risk; `run_resolve_changed` then re-solves each and diffs its bucket against the committed DB, exiting **NO-GO** on any backward move. `changed_emit_artifacts.py --since-commit <Day-0 SHA> --format json/markdown` is the same at-risk list for the checkpoint.

**Readiness: ✅ READY — no extension.** Allowlists current (#1439/#1461 open); `--resolve-changed` covers both the widened-VARIABLE presolve and the head-offset cold goldens.

---

## Tool 4 — AD property-test catalog (`test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/`)

**New class to cover:** the **head-domain-offset** cross-term shape (Category 1, robert/mine) needs a property-test guard; and the reverted offset-alias fix (himmel16/polygon P5) must have its fixtures ready to flip from xfail to passing when the fix lands.

**Audit — fixtures + test run (this task):**

- **8 fixtures present** (`shape1`–`shape8`); test run = **7 passed, 1 xfailed** (2.44 s). `shape8_offset_alias_successor` is **xfail-strict** (`#1143/#1447: reverted; pending coupled distance-Jacobian fix (Sprint 30)`); `shape7_offset_alias_cyclic` **passes** as a structural-decomposition guard for the himmel16 `i++1` cyclic shape (#1146 — its residual `2.0` numeric defect is noted as not assertable without a GAMS residual eval).
- **The head-domain-offset shape is the one genuinely-missing fixture** — none of `shape1`–`shape8` covers the `nu_sb`/`lam_pr` head-offset cross-term (shape8 is the *offset-alias* successor, a distinct Category-5 shape). P8 adds one new `shape9`-style head-offset fixture (a minimal synthetic `sb(r,tt+1)`-shaped equation asserting the `stat_x` cross-term references the head-labeled multiplier).
- **The catalog is structurally extensible** — adding a fixture is: drop a `.gms` into `tests/fixtures/crossterm_shapes/` + add a `def test_shape9_...` that calls the existing `_emit(...)` / `_stat_row(...)` helpers. No refactor. Enabling `shape8` (and any residual `shape7` numeric assertion) once the offset-alias fix lands is a one-line drop of `@pytest.mark.xfail`.

**Readiness: ✅ READY — no structural blocker.** The catalog covers the offset-alias shapes today (shape7 passing, shape8 xfail-pending-fix); the head-offset fixture is a clean one-file add for P8, and shape8 flips to passing by removing its xfail marker when the #1143 fix lands.

---

## Gap List

**One optional, non-blocking ≤ 1 h extension; otherwise NONE.** The Sprint-28/29 tools cover the Sprint-30 classes; the in-sprint diagnosis runs on tooling that already handles the cases.

| Tool | New Sprint-30 class | Verdict | Day-0 extension |
|---|---|---|---|
| `kkt_residual.py` | head-offset `nu_sb`/`lam_pr` multipliers | dual-transfer **CONSISTENT** on robert + mine; per-row localization carries a same-index-transfer artifact on base-normalized head-offset equations | **OPTIONAL ≤ 1 h** — head-label multiplier warm-start (`nu_<eq>.l(idx)=<eq>.m(head(idx))`) for the per-row residual; **non-blocking** (cold-solve control is the standing mitigation, Task 3) |
| `check_presolve_divergence.py` | Class-B CGE `stat_pz` + cold-convex residue | soft `obj_gap` (gates on embedded NLP, not the MCP); no false hard-fail | none |
| `check_golden_staleness.py` + allowlists | widened-VARIABLE + head-offset regens | allowlists current (#1439/#1461 open) | none |
| `run_full_test.py --resolve-changed` | widened-VARIABLE presolve + head-offset cold goldens | both suffixes covered (`_mcp_presolve.gms`, `_mcp.gms`) | none |
| `test_ad_crossterm_shapes.py` | head-domain-offset shape | 7 passed / 1 xfailed; head-offset fixture is a clean one-file add; shape8 flips on fix | none (P8 adds the fixture) |

**Bottom line:** proceed to Sprint 30 Day 1 on the existing tooling. The one optional harness extension (head-label warm-start) may be picked up Day-0 if the team wants trustworthy per-row localization on head-offset models; otherwise the cold-solve control experiment (Task 3) is the standing, proven method and no code change is required.

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md && echo present
# Harness dual-transfer on the two head-offset-multiplier carryforwards (expect CONSISTENT):
for m in robert mine; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "dual transfer"; done
# --resolve-changed covers both golden suffixes:
grep -n "_GOLDEN_SUFFIXES" scripts/gamslib/run_full_test.py
# Property catalog (expect 7 passed, 1 xfailed):
.venv/bin/python -m pytest tests/integration/emit/test_ad_crossterm_shapes.py -q 2>&1 | tail -1
# Allowlists current (7 + 1) and their issues still open:
grep -cvE '^[[:space:]]*(#|$)' scripts/sprint_audit/golden_staleness_allowlist.txt   # 7
grep -cvE '^[[:space:]]*(#|$)' scripts/diagnostics/presolve_divergence_allowlist.txt # 1 (korcge, #1439 open)
```
