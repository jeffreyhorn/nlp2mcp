# Sprint 29 — Reusable-Tooling Readiness Audit

**Task:** Sprint 29 Prep Task 6 (audit-only — read-only tool runs, zero `src/` diff)
**Date:** 2026-06-27
**Scope:** the three diagnostic/CI tools Sprint 28 built and Sprint 29 reuses, audited against the new Sprint-29 model classes (presolve `_fx_`-multiplier warm-starts, head-domain-offset multipliers, the cold-convex cohort, offset-alias gradients).
**Verdict:** **all three tools are ready — gap list = NONE.** No Day-0 extension is required before Sprint 29 Day 1.

---

## Tool 1 — `kkt_residual.py` (KKT-residual harness)

**New classes to cover:** the presolve `_fx_`-multiplier warm-start (`nu_<var>_fx_<idx>`, rocket #1462) and the head-domain-offset multipliers (`lam_pr` at the `l+1` lead, mine #1443). The risk (Unknowns 1.2 / 2.4): if the dual-transfer self-check mis-maps these synthetic multipliers, every rocket/mine verdict is unreliable.

**Audit (Task 4 + this task):**

| Model | Class | `dual_transfer.consistent` | Verdict |
|---|---|---|---|
| **rocket** | presolve `_fx_` multipliers | **True** | Case b, `stat_step` 0.497 |
| **mine** | head-domain-offset (`lam_pr` at `l+1`) | **True** | Case b, `stat_x('4','1','1')` 1.33 |

The `--nlp-presolve` emit already loads **all** multiplier classes into the MCP warm-start (`nu_<eq>.l = eq.m`, `lam_<eq>.l = abs(eq.m)`, `piL/piU` from variable marginals — and the `_fx_` equations are just ordinary equality rows from the harness's view), so the dual-transfer self-check (§2 of the harness design) validates them with **no special-casing**. Both Sprint-29 carryforwards report **CONSISTENT** — the per-row residual the harness then reads is trustworthy.

**Readiness: ✅ READY — no extension.** The harness handles `_fx_` and head-offset multipliers without a Day-0 index-mapping change.

---

## Tool 2 — `check_presolve_divergence.py` (embedded-NLP divergence detector)

**New class to cover:** the **cold-convex cohort** (the ~24–30 warm-start-only models) is *expected* to diverge cold; the detector must classify that as a **soft `obj_gap` (informational)**, not a hard-fail, or the Day-5/Day-10 checkpoints flood. Also: is rocket #1462 correctly handled (allowlisted or soft)?

**Audit (read-only detector runs):**

| Model | Class | Detector result | Hard-fail? |
|---|---|---|---|
| **rocket** | presolve `_fx_` (#1462) | **OBJ-GAP (info, review)** — embedded 1.0 vs ref 1.0128 (rel 0.0126), "possibly a benign non-convex local optimum" | **No** |
| **maxmin** | cold-convex cohort (Case-b lead) | no divergence, 0 obj-gap | No |
| **catmix** | cold-convex cohort | no divergence, 0 obj-gap | No |

The detector's DB-reference + hard-fail-only-on-abort/infeasible-embedded logic (the Sprint-28 rework) correctly **soft-classifies** the cohort and rocket. **rocket does NOT need allowlisting** — it surfaces as an informational `obj_gap`, not a hard divergence (the embedded NLP solves; only the *MCP* is MS-5, which the detector does not gate on). The cohort produces 0 false hard-fails on the sample (confirming the Task-3 Unknown-4.4 finding).

**Readiness: ✅ READY — no extension, no new allowlist entry.** The cold-convex cohort + rocket soft-classify; the Day-5/Day-10 checkpoints will not flood.

---

## Tool 3 — `check_golden_staleness.py` + allowlists + `changed_emit_artifacts.py`

**New class to cover:** Sprint-29 emit-touching PRs (the offset-alias gradient fix, the `_fx_` warm-start, the head-offset re-derivation) will regenerate goldens; the staleness gate + the changed-golden diff must (a) not flap on the known cross-platform / out-of-scope models and (b) feed the right changed-golden set into the Task-8 checkpoint re-solve.

**Audit (allowlist review + issue-state check):**

- **Golden-staleness allowlist** (`scripts/sprint_audit/golden_staleness_allowlist.txt`): **7 entries, all still valid** — 3 multi-solve drivers (danwolfe, decomp, saras) + 3 discrete MIP/MINLP (nemhaus, nonsharp, trnspwl) + **indus** (cross-platform byte non-determinism, #1461). Matches the "6 out-of-scope + indus" expectation; no Sprint-28 fix made any of them in-scope again.
- **Presolve-divergence allowlist** (`scripts/diagnostics/presolve_divergence_allowlist.txt`): **1 entry — korcge** (#1439, embedded `$include` `EXECERROR=5`).
- **Issue states:** **#1439 (korcge) OPEN** and **#1461 (indus) OPEN** — both allowlist entries are still tracking live deferred bugs, so neither should be removed.
- **`changed_emit_artifacts.py`** is the **right Task-8 checkpoint re-solve input:** `--since-commit <Sprint-29-Day-0-SHA>` groups every changed `*_mcp.gms` / `*_mcp_presolve.gms` by triggering commit (with `--format json`/`markdown` for downstream tooling) — exactly the at-risk-golden list the Day-5/Day-10 re-solve consumes.

**Readiness: ✅ READY — no extension.** Allowlists current; the changed-golden diff is the Task-8 input.

---

## Gap List

**NONE.** All three Sprint-28 tools already cover the Sprint-29 model classes; no Day-0 extension (harness index-mapping, detector tolerance/allowlist, or staleness allowlist edit) is required before Day 1. The in-sprint diagnosis runs on tooling that already covers the cases.

| Tool | New Sprint-29 class | Verdict | Day-0 extension |
|---|---|---|---|
| `kkt_residual.py` | `_fx_` + head-offset multipliers | dual-transfer CONSISTENT on rocket + mine | none |
| `check_presolve_divergence.py` | cold-convex cohort + rocket | soft `obj_gap`, no hard-fail | none |
| `check_golden_staleness.py` | Sprint-29 emit regens | allowlists current (#1439/#1461 open) | none |

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md && echo present
# Harness dual-transfer on the two new-multiplier-class carryforwards:
for m in rocket mine; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "dual transfer"; done
# Detector soft-classifies rocket + a cohort sample (no hard-fail):
for m in rocket maxmin catmix; do .venv/bin/python scripts/diagnostics/check_presolve_divergence.py --model $m 2>&1 | tail -1; done
# Allowlists current:
grep -cvE '^\s*#|^\s*$' scripts/sprint_audit/golden_staleness_allowlist.txt   # 7 (6 OOS + indus)
grep -cvE '^\s*#|^\s*$' scripts/diagnostics/presolve_divergence_allowlist.txt # 1 (korcge)
```
