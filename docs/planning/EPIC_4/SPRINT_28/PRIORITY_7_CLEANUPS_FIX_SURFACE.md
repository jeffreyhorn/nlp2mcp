# Priority 7 — Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385)

**Task:** Sprint 28 Prep Task 9 (fix-surface analysis only — the fixes are implemented in-sprint)
**Date:** 2026-06-11
**PR24 note:** every candidate `file:line` below is a **Day-0-trace hypothesis**, not an established surface — the in-sprint work establishes the surface by a trace before any `src/` change.

---

## #1374 — robot `.l` denominator/override dedup (Unknown 7.1)

### The double-emission

robot's `rho.l('h0') = 4.5;` (through `rho.l('h9')`, and `rho.l('h50')`) is emitted **twice**:
1. the **denominator-init block** — expands the source `rho.l(h) = 4.5;` (a div-by-zero guard so `rho` is non-zero before the solve);
2. the **`fx_to_l_override`** — from the source `rho.fx(firstlast) = 4.5;`, the `fx_to_l_overrides_by_var` integration (Sprint 25 #1349) emits the same `rho.l(...) = 4.5;`.

Last-write-wins with the same numeric value, so it is **functionally harmless** — pure byte-stability / diff-noise. robot is `path_solve_license` (failing), so **no Solve/Match impact**.

### Isolation from the Sprint 27 fix — **ISOLATABLE** (the 7.1 answer)

The Sprint 27 Day-13 fix handled the **`.fx`-restore** shape (otpop/dinam): a suppressed-`_fx_` equation's value emitted in BOTH the "Variable Bounds" pass (`emit_gams.py` ~1726) AND the "suppressed-fx restore" pass (~2825); the fix skips the Variable-Bounds emission. The robot `.l` shape is a **different mechanism** — the denominator-init block + the `fx_to_l_overrides_by_var` integration, not the `.fx`-restore pass — so the dedup is **isolatable** (no shared code path with the Sprint 27 fix; no regression risk to otpop/dinam).

### Candidate fix surface (Day-0-trace hypothesis)

`src/emit/emit_gams.py`, the `fx_to_l_overrides_by_var` integration in the variable-init emission (the `_emit_var_inits`-area pass): **suppress the override emission when its `(var, element, value)` matches a denominator-init `.l` assignment already emitted for that element** (the check ISSUE_1374 §"Recommended fix" already sketches for the analogous stdcge/twocge symptom). Day-0 trace: locate both robot `rho.l('h0')` emission sites; confirm they are the denominator-init pass and the override pass.

**Estimate:** ~1–2h (isolated emit-time dedup + robot golden regen; robot stays `path_solve_license`). **Coupling risk: LOW** (distinct from the Sprint 27 fix).

---

## #1400 — `message`-field captured-warning path leak (Unknown 7.2)

### Where the second leak is (the 7.2 answer)

The Sprint 27 #1400 fix relativized the **`mcp_file_used`** field (a single path) via `_repo_relative_path` in `run_full_test.py`. The **second** leak is the free-text **`message`** field, populated from a captured subprocess **stderr**:

- `scripts/gamslib/batch_translate.py:279` — on a failed translate, `error_msg = stderr if stderr else stdout`;
- `:285` — `"message": error_msg[:500]` is stored into `gamslib_status.json`.

When `src` emits a `warnings.warn(...)` (e.g. `src/ad/index_mapping.py:502/544/559`, `src/kkt/stationarity.py:5694`), Python's **default warning formatter** writes `<absolute-path>:<lineno>: UserWarning: <message>` to stderr — so an absolute `/Users/.../src/…py:NNN` lands in the DB `message` whenever a model **emits a warning AND fails translate** in the same run. The same capture shape exists on the solve path (`run_full_test.py:550`, `"message": result.get("error", …)`).

### DB audit (the 7.2 evidence)

The **current committed `gamslib_status.json` is clean** — 0 absolute-path substrings (`/Users/…`, `src/…py:NNN`) in any field. The leak is **transient**: it surfaces only for the specific warn-then-fail combination in a given run, which the committed DB does not currently contain (e.g. mine's `message` is now the clean `Model: Infeasible (status 4)`). So #1400-second is a latent machine-portability defect, not a present corruption.

### Candidate fix surface (Day-0-trace hypothesis)

Two candidates (the Day-0 trace picks one):
- **(a) at the capture site** — relativize abs-path substrings in `error_msg` before storing (a regex strip of the `_REPO_ROOT` prefix applied to the *text*, broader than the single-path `_repo_relative_path`); applied at `batch_translate.py:279–285` **and** the solve-path `run_full_test.py:550`.
- **(b) at the source (cleaner)** — install a repo-relative `warnings.formatwarning` (or set `PYTHONWARNINGS`) in `src/cli.py` so emitted warnings never contain the absolute path; this fixes every downstream consumer at once.

**Estimate:** ~1–2h (scripts-only for (a); (b) touches `src/cli.py`). **Coupling risk: LOW.** To reproduce the leak for the acceptance test, force a warn-then-fail model and assert no `/Users/` substring in the captured `message`.

---

## #1385 — runtime-guard eq-body re-emit + `J_gᵀ·lam` cross-terms (Unknown 7.3)

### Atomic landing — **REQUIRED** (the 7.3 answer)

Sprint 27 Day 7 landed the **translate-time-only** short-circuit (`src/ad/index_mapping.py` `_is_blowup_dynamic_subset_equation`, srpchase 846s→6.56s) and **deferred two coupled pieces**:
1. the **runtime-guard equation-body re-emit** (`src/kkt/stationarity.py`) — re-emit the skipped `slack`/`demand` constraints as `sum(<bound>$(<predicate>), <body>)` runtime-guarded GAMS equations so they appear in the MCP;
2. the **`J_gᵀ·lam` cross-terms** — those equations' contributions to every variable's stationarity (`∂slack/∂y·nu_slack`, etc.), which the AD layer currently enumerates as ZERO instances for the skipped equations.

ISSUE_1385 states it directly: **re-emitting the constraints (1) WITHOUT the cross-terms (2) creates an inconsistent MCP (multipliers with no complementarity coupling), so both land together.** The Day-4 reverted impl is the cautionary evidence: it produced `nu_slack("srn")` / `lam_demand("srn")` with `srn` a **set name** (not an element of `n`) and dropped the `J_gᵀ·lam_demand` cross-terms (Jacobian entries vanished when the symbolic index didn't match concrete elements in `_diff_varref`). **Atomic: confirmed.**

### Candidate fix surface (Day-0-trace hypothesis)

`src/kkt/stationarity.py` (the runtime-guard re-emit) **coupled with** the AD Jacobian cross-term construction (`src/ad/constraint_jacobian.py` / `_diff_varref` — where symbolic-instance indices currently drop to 0). This is the **symbolic-instance handling** the Day-4 impl got wrong, so it is **larger than a typical cleanup**.

### Re-scope flag

This is the deferred *redesign* half of #1385, not a small dedup like #1374/#1400 — it affects 5 `translate_timeout` models (srpchase, iswnm, sarf, mexls, nebrazil) but yields **no firm Solve/Match this sprint** (Sprint 27's recovery was translate-only; downstream solve gains are not projected). **Recommendation:** treat #1385 as a **re-scope candidate** — if the Day-0 trace confirms the cross-terms require the same symbolic-instance AD rework that blocked the Day-4 impl, it should be sequenced as its own focused workstream (or deferred to Sprint 29) rather than landed as a Priority-7 cleanup. **Estimate:** larger — ~6–10h if it stays in-sprint (the cross-term/symbolic-instance work is the Day-4 revert blocker), vs the ~1–2h each for #1374/#1400. **Coupling risk: HIGH** (the re-emit and cross-terms are atomic; the cross-terms are the hard part).

---

## Summary — per-item estimate (feeds the Task 10 schedule)

| Item | Candidate surface (hypothesis) | Coupling risk | Estimate | Solve/Match impact |
|---|---|---|---|---|
| **#1374** robot `.l` dedup | `emit_gams.py` `fx_to_l_overrides_by_var` integration (suppress override when it matches the denominator-init `.l`) | LOW — isolatable from the Sprint 27 `.fx`-restore fix | ~1–2h | none (byte-stability only; robot stays `path_solve_license`) |
| **#1400** message path leak | `batch_translate.py:279–285` (+ `run_full_test.py:550`) relativize stderr text, OR a repo-relative `warnings.formatwarning` in `src/cli.py` | LOW | ~1–2h | none (machine-portability) |
| **#1385** runtime-guard re-emit + cross-terms | `stationarity.py` re-emit **+** `constraint_jacobian.py`/`_diff_varref` cross-terms — **atomic** | HIGH — atomic; symbolic-instance AD rework (Day-4 revert blocker) | ~6–10h | translate-only (no firm Solve/Match); **re-scope candidate** |

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md && echo present
grep -Ei '#1374|#1400|#1385|robot|message|srpchase' docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md | head
grep -iE 'hypothes|Day-0 trace' docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md
```
