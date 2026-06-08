# Emitter: Redundant Duplicate Variable Initializations in Regenerated MCP Artifacts

**GitHub Issue:** [#1374](https://github.com/jeffreyhorn/nlp2mcp/issues/1374)
**Status:** PARTIALLY FIXED (Sprint 27 Day 13, 2026-06-08) — the dominant `.fx`-restore duplicate shape is fixed (otpop, dinam); the remaining `.l` denominator/override shape (robot) is deferred to Sprint 28. See "Sprint 27 Day 13 audit + fix" below.
**Severity:** Low — functionally harmless at runtime (last-write-wins, same numeric value), but degrades the byte-stability surface and adds diff noise on regenerated artifacts. One sub-symptom (rocket clamp-clobber) was actually a latent silent-correctness bug; PR #1373's regeneration fortuitously fixed it via reordering.
**Date:** 2026-05-09
**Last Updated:** 2026-06-08 (Sprint 27 Day 13 — corpus audit + `.fx`-restore-shape fix; `.l` shape → Sprint 28)
**Affected Models:** otpop, dinam (`.fx`-restore duplicate — FIXED); robot (`.l` denominator/override duplicate — Sprint 28). (Prior-doc stdcge/twocge `pf.l` no longer present in the current-emit audit.)
**Target Sprint:** Sprint 27 (dominant shape) + Sprint 28 (remaining `.l` shape)

## Sprint 27 Day 13 audit + fix (2026-06-08)

**Corpus audit** (exact-byte-duplicate per-element init lines across all 153 cold `*_mcp.gms` goldens): **3 models**, 13 duplicate lines, in 2 shapes:

| Model | dups | shape |
|---|---|---|
| otpop | 9 | `x.fx('1965') = 29.4;` … `'1973'` — **`.fx`-restore** |
| dinam | 2 | `sav.fx('1968') = 52.1;`, `gdp.fx('1968') = 260.9;` — **`.fx`-restore** |
| robot | 2 | `rho.l('h0') = 4.5;`, `rho.l('h50') = 4.5;` — **`.l` denominator/override** |

**`.fx`-restore shape — FIXED** (`src/emit/emit_gams.py`). For a per-element `fx_map` entry whose `_fx_` equation is **suppressed** AND whose variable carries a stationarity condition, the value is emitted in BOTH the "Variable Bounds" section (line ~1726) AND the "Fix suppressed _fx_ equations" restore pass (line ~2825). The restore pass re-emits the value *after* the blanket `var.fx(...) = 0` from stationarity, so it is the single correct (blanket-surviving) emission; the Variable Bounds emission is a byte-identical duplicate. Fix: skip the Variable Bounds emission when `eq_name in suppressed_fx and var_name in kkt.stationarity_conditions`. otpop/dinam regenerated (otpop −9 lines, pure dedup; dinam −2 dedup lines, plus a pre-existing `comp_up_fdp(te)→(t)` staleness refresh that is independent of this fix). otpop still compiles clean + `model_infeasible` (unchanged); matching models (qdemo7/cesam2/korcge/launch) byte-identical.

**`.l` denominator/override shape — Sprint 28.** robot's `rho.l('h0') = 4.5;` is emitted by both the denominator-init block (avoid div-by-zero; expands source `rho.l(h) = 4.5`) and the `fx_to_l_override` (from `rho.fx(firstlast) = 4.5`). This is a distinct mechanism (`.l`, not `.fx`-restore) and is **deferred to Sprint 28** per the Day-13 "most-common-1–2-shapes" scope. robot is `path_solve_license` (failing), so the duplicate has no Solve/Match impact.

---

## Problem Summary

The emitter generates redundant or out-of-order variable initializations in three observed shapes. PR #1373 (Sprint 26 Prep Task 9 baseline regeneration) surfaced these in the diff: the regeneration didn't introduce the bugs — the duplicates were present pre-regeneration too, and the regeneration only reordered them. But the visible diff highlights three real emit-cleanup opportunities.

---

## Symptom 1 — Duplicate `pf.l` initialization (stdcge, twocge)

### stdcge_mcp.gms (line ~308)

```
pf.l('CAP') = 1.0;
pf.l('LAB') = 1.0;
pf.l('LAB') = 1;          <-- duplicate of the line above
```

PR #1373 diff:

```diff
-pf.l('LAB') = 1;
 pf.l('LAB') = 1.0;
+pf.l('LAB') = 1;
```

### twocge_mcp.gms (multi-region variant, line ~345)

```
pf.l('CAP','JPN') = 1.0;
pf.l('CAP','USA') = 1.0;
pf.l('LAB','JPN') = 1.0;
pf.l('LAB','USA') = 1.0;
pf.l('LAB','JPN') = 1;    <-- duplicate of the line two above
pf.l('LAB','USA') = 1;    <-- duplicate of the line two above
```

PR #1373 diff:

```diff
-pf.l('LAB','JPN') = 1;
-pf.l('LAB','USA') = 1;
 pf.l('LAB','JPN') = 1.0;
 pf.l('LAB','USA') = 1.0;
+pf.l('LAB','JPN') = 1;
+pf.l('LAB','USA') = 1;
```

### Functional impact

- **Runtime:** harmless (last-write-wins, same value `1.0` ≡ `1`).
- **Byte stability:** the two assignments use different numeric literal formats (`1.0` vs `1`); diff and byte-stability tooling sees this as material churn.
- **PR review:** every regeneration that touches stdcge/twocge surfaces the duplicate as a "what changed?" question.

---

## Symptom 2 — Clamp violated by post-clamp boundary override (rocket)

### rocket_mcp.gms (lines ~107-109, post-PR-#1373 regeneration)

```
v.l(h) = (ord(h) - 1) / nh * (1 - (ord(h) - 1) / nh);
v.l(h) = min(max(v.l(h), 1e-6), v.up(h));   /* clamp to [1e-6, v.up(h)] */
v.l('h0') = 0;                              /* boundary condition (intentional) */
```

PR #1373 diff:

```diff
-v.l('h0') = 0;
 v.l(h) = (ord(h) - 1) / nh * (1 - (ord(h) - 1) / nh);
 v.l(h) = min(max(v.l(h), 1e-6), v.up(h));
+v.l('h0') = 0;
```

### Functional impact

- **Pre-PR-#1373 ordering** was a **silent correctness bug**: `v.l('h0') = 0` was emitted BEFORE the clamp. The `min(max(..., 1e-6), ...)` clamp would silently override the boundary 0 to 1e-6, defeating the rocket model's intentional h0 boundary condition.
- **Post-PR-#1373 ordering** is correct: `v.l('h0') = 0` is emitted AFTER the clamp, so the explicit boundary value survives.
- **Readability:** even though the new ordering is correct, the emit structure makes the intent unclear. A reader sees `v.l(h) = min(max(..., 1e-6), ...)` immediately followed by `v.l('h0') = 0` and reasonably questions whether the boundary 0 conflicts with the `>= 1e-6` clamp. The ordering-implicit "clamp interior, then re-fix boundaries" intent is not visible from the emitted lines alone.

---

## Likely Root Cause

All three symptoms appear to be in the same Sprint 25 #1349 ("per-instance `.l` override post-init integration") emit-ordering family. The emitter generates two distinct emission groups:

1. **Generic POSITIVE / FREE / clamp init** — applies to all elements of the variable's domain.
2. **Per-instance `.l = expr` override** — from explicit per-element initializations or `.fx`-replaced overrides.

When both groups touch the same variable element (e.g., `pf('LAB')` gets both a generic `= 1.0` and an explicit per-instance `= 1`), the emitter writes both lines without dedup. Sprint 25 #1349 fixed the override-integration ORDERING (per-instance overrides now go AFTER the generic init group, fixing the rocket clamp-clobber); it did not add deduplication for cases where the override and the generic init produce the same value.

Candidate fix sites in `src/emit/emit_gams.py`:

- Variable bounds / init group emission — currently emits both `bulk POSITIVE init = default` and per-element `.l = expr` overrides.
- Sprint 25 PR #1360 / Issue #1349 follow-up: `fx_to_l_overrides_by_var: dict[str, list[str]]` integration before the topological sort. Adding a "if override value matches the bulk init default, suppress the override emission" check would fix Symptoms 1 (stdcge / twocge).
- For Symptom 2 (rocket): emit the clamp body to skip explicitly-fixed boundary points (e.g., `v.l(h)$(not boundary) = min(...)`), OR add an emit comment annotation explaining that explicit boundary overrides are emitted post-clamp.

---

## Proposed Fix Approaches

### Approach A — Suppress duplicate when override matches bulk-init default (recommended for Symptom 1)

When the per-instance override's emitted value (after format normalization) equals the bulk POSITIVE / FREE init, suppress the override emission entirely. Catches the stdcge / twocge `pf.l('LAB') = 1` vs `= 1.0` case directly.

**Implementation sketch:**
```python
# In src/emit/emit_gams.py, in the per-var init-group integration:
if normalized(override_value) == normalized(bulk_init_default):
    skip_override_emission()
```

`normalized()` should canonicalize numeric formats (`1` → `1.0` or vice-versa) so the dedup doesn't depend on formatting.

### Approach B — Comment-annotate the post-clamp boundary overrides (recommended for Symptom 2)

Either:
- Skip the clamp body for explicitly-fixed boundary points: `v.l(h)$(not (sameas(h, 'h0') or ...)) = min(max(...), ...);`
- Add an explicit comment: `* Note: explicit boundary overrides below are intentionally post-clamp` immediately before the override block.

The skip-clamp variant is structurally cleaner; the comment variant is a smaller change.

---

## Tests to Add

- **Unit test** in `tests/unit/emit/`: synthetic `ModelIR` with a variable that has both a bulk POSITIVE init `= 1.0` and a per-instance override `= 1`. Assert the emitted `_mcp.gms` contains exactly one assignment (the bulk init) and the override is suppressed.
- **Unit test** for the rocket case: synthetic `ModelIR` with a variable that has a clamp `min(max(..., 1e-6), ...)` and a per-instance boundary override `= 0`. Assert the emitted code either (a) skips the clamp for the boundary point or (b) includes the explanatory comment.
- **Regression test (byte-stability):** regenerate `data/gamslib/mcp/stdcge_mcp.gms` and `twocge_mcp.gms` and assert no duplicate `pf.l('LAB'*)` lines.

---

## Files Involved

- `src/emit/emit_gams.py` — variable bounds / init group emission (likely `_emit_var_inits` or similar function around the `fx_to_l_overrides_by_var` integration from Sprint 25 #1349)
- `data/gamslib/mcp/stdcge_mcp.gms`, `twocge_mcp.gms`, `rocket_mcp.gms` — affected artifacts (will regenerate cleanly after fix)

---

## Estimated Effort

**2–4h focused** for both symptoms, plus a corpus regeneration sweep to verify no other affected models. The byte-stability harness (PR12) will surface any other models with similar duplicates once enforced.

---

## Scope and Sprint Routing

- **Out of scope for Sprint 26** (which is focused on Pattern C generalization, AD residuals, and translation-timeout work — not emitter cleanup).
- **Candidate for Sprint 27** alongside the planned PR12 byte-stability enforcement work — the duplicate-emit issue specifically degrades the byte-stability surface, so addressing it before enforcing per-model byte-stability avoids creating false-positive failures.
- The advisory `.gms` artifact policy in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §6 and `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` §6 explicitly notes that regenerated artifacts are advisory until PR12 byte-stability enforcement lands; that policy makes #1374 a non-blocker for Sprint 26.

---

## Related

- **PR #1373** (Sprint 26 Prep Task 9) review comments where these were surfaced: 3213940810 (stdcge), 3213940815 (twocge), 3213940819 (rocket).
- **#1349** (Sprint 25 Day 14) — `fx_to_l_overrides_by_var` integration that fortuitously fixed the rocket clamp-clobber via reordering; the duplicate-emit issue is the same emit family.
- **#1360** (Sprint 25 PR review fix) — clearlak `.l` override post-init integration; same family.
- **PR12** (Sprint 25 #1283 + byte-stability harness) — the canonical reference for byte-stability enforcement; #1374 should land before per-model byte-stability is enforced for the broader corpus.
- **`docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md`** §6 — advisory `.gms` artifact policy that scopes #1374 out of Sprint 26.
