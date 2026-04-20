# Catalog — Emitter / Stationarity Bug Backlog (#1275–#1281)

**Created:** 2026-04-20
**Sprint:** 25 (Prep Task 4)
**Issues:** #1275, #1276, #1277, #1278, #1279, #1280, #1281
**Cross-reference:** [`AUDIT_ALIAS_AD_CARRYFORWARD.md`](AUDIT_ALIAS_AD_CARRYFORWARD.md) (Task 2), [`INVESTIGATION_PARSER_NON_DETERMINISM.md`](INVESTIGATION_PARSER_NON_DETERMINISM.md) (Task 3)

---

## Executive Summary

The 7 Sprint 24 Day 13 review findings cluster into **3 code-path families**, not 3 independent buckets:

- **Emitter (`src/emit/`)**: 4 issues — #1275 (presolve `$include`), #1276 (fawley `.fx` dedup), #1280 (UEL quoting), #1281 (lmp2 `Parameter` dedup).
- **IR normalization (`src/ir/normalize.py`)**: 1 issue — #1279 (robustlp scalar-equation widening).
- **Stationarity / AD (`src/kkt/stationarity.py`, `src/ad/`)**: 2 issues — #1277 (twocge `stat_tz` mixed offsets), #1278 (twocge `ord(r) <> ord(r)` tautology).

**Subsume opportunities identified (primary finding):**

1. **#1275 + #1281 share the `_emit_nlp_presolve` path** in `src/emit/emit_gams.py:889`. Both are about what that function emits around its `$include` line. A single fix pass can address both (correct `Path.resolve()` → repo-relative, and audit interaction with the wrapper's `$onMultiR`/`$offMulti` scope for lmp2).
2. **#1276 + #1281 share the "emitter idempotency" structural pattern**. Different emission functions (multiplier `.fx` vs parameter declarations) but the fix shape is the same: track already-emitted `(symbol_name, domain, condition)` tuples and skip duplicates. Worth landing a shared `_DeclaredSymbolTracker` helper rather than bespoke-deduping each site.
3. **#1277 is partially subsumed by Task 2's Pattern C fix**. Same offset+alias bug family as polygon (#1143) and himmel16 (#1146). Expected to improve after Pattern C lands; may need one small extension to `_apply_alias_offset_to_deriv` in `src/kkt/stationarity.py:1743` to cover variable operands (not just `ParamRef`) in the offset group.
4. **#1278 is NOT subsumed by Task 2**. The `ord(r) <> ord(r)` tautology is a distinct substitution bug (guards rewritten alongside body references during instance enumeration), separate from the derivative-chain logic Pattern A/C fix touches.

**Proposed 3-batch fix order:**

| Batch | Days | Issues | Effort | Rationale |
|---|---|---|---|---|
| 1 | Day 1–2 | #1275, #1280 | 3–5h | Quick emitter fixes with zero interaction with alias-AD; can ship alongside Priority 1 start |
| 2 | Day 3–4 | #1279, #1276, #1281 | 7–9h | IR-normalize fix (#1279) unblocks robustlp; emitter-dedup pair (#1276, #1281) shares the symbol-tracker helper |
| 3 | Day 5–7 | #1277 post-Pattern-C verification, #1278 | 2–4h | #1277 validated after Pattern C; #1278 fix is a standalone substitution-preservation patch |

**Total:** 12–18h — matches the Sprint 24 retrospective's estimate bound.

**Cross-reference to Task 2 alias-AD fix:**

- **#1277 subsumed by Pattern C fix?** Partially — Pattern C's `_alias_match` extension reaches the derivative chain but twocge's mixed `mu(j+1,r) * pq(j,r)` output suggests `_apply_alias_offset_to_deriv` needs extension from ParamRef-only to also cover VarRef operands in an offset group.
- **#1278 subsumed?** No. Different code path (instance-enumeration substitution, not derivative chain).

---

## Section 1 — Per-Issue Classification

Each row includes the code path, expected fix surface, effort, and whether the issue is subsumed-by / adjacent-to another fix.

| # | Issue | Model | Severity | Code Path | Fix Site (specific) | Est. | Subsume | Batch |
|---|---|---|---|---|---|---|---|---|
| #1275 | Presolve `$include` absolute paths | robustlp, chain, mathopt3 (any `--nlp-presolve` model) | High | **Emitter** | `src/emit/emit_gams.py:933` (`Path(source_file).resolve().as_posix()`) | 2–3h | Shares site with #1281 | 1 |
| #1276 | fawley duplicate `.fx` emission | fawley (springchain historical) | Low | **Emitter** | `src/emit/emit_gams.py` or `src/emit/equations.py` multiplier-fixation path (TBD — needs call-site logging) | 1–2h | Shares pattern with #1281 | 2 |
| #1277 | twocge `stat_tz` mixed offsets | twocge | Medium | **Stationarity / AD** | `src/kkt/stationarity.py:1743` (`_apply_alias_offset_to_deriv`), extend from ParamRef-only to VarRef operands in offset groups | 1–2h (after Pattern C) | Partially subsumed by Task 2 Pattern C | 3 |
| #1278 | twocge `ord(r) <> ord(r)` tautology | twocge | Medium | **Stationarity / AD** | `src/kkt/stationarity.py` instance-enumeration substitution (guards incorrectly rewritten); OR a sibling pass that preserves summation index distinct from bound reference | 3–4h | NOT subsumed by Task 2 | 3 |
| #1279 | robustlp `defobj(i)` scalar-widening | robustlp | High | **IR normalize** | `src/ir/normalize.py::normalize_model` equation-domain inference | 3–4h | Standalone | 2 |
| #1280 | mathopt4 unquoted UELs (`x1.l`) | mathopt4 | Medium | **Emitter** | `src/emit/*.py` `nlp2mcp_uel_registry` declaration emitter — add unconditional `'...'` quoting | 1–2h | Standalone (no interaction) | 1 |
| #1281 | lmp2 duplicate `Parameter` | lmp2 | High | **Emitter** | `src/emit/emit_gams.py:_emit_nlp_presolve` scope interaction with `src/emit/original_symbols.py` parameter emission | 2–3h | Shares `_emit_nlp_presolve` site with #1275; shares dedup pattern with #1276 | 2 |

**Totals by code path:**

- Emitter: 4 issues (#1275, #1276, #1280, #1281) — 6–10h
- IR normalize: 1 issue (#1279) — 3–4h
- Stationarity / AD: 2 issues (#1277, #1278) — 4–6h (mostly dependent on Task 2 landing first)

---

## Section 2 — Shared Code Paths and Subsume-Opportunities

### 2.1 `_emit_nlp_presolve` cluster (#1275, #1281)

**Shared site:** `src/emit/emit_gams.py:889–940` (`_emit_nlp_presolve`).

**Current structure (verified via grep):**

```python
# src/emit/emit_gams.py:931–937
from pathlib import Path
abs_path = Path(source_file).resolve().as_posix()       # <-- #1275 bug: absolute path
escaped_include_path = abs_path.replace('"', '""')
sections.append("$onMultiR")
sections.append(f'$include "{escaped_include_path}"')   # <-- emits absolute path in artifact
sections.append("$offMulti")
```

- **#1275 fix:** replace `Path(source_file).resolve().as_posix()` with a repo-relative path resolver, or emit an `%NLP2MCP_SRC%` macro with a sensible default. This is a single-line change with supporting test fixture under `tests/unit/emit/`.
- **#1281 context:** the `$include` is wrapped in `$onMultiR ... $offMulti`, which is supposed to allow re-declaration of symbols. But lmp2's pipeline state shows `Parse error: no_solve_summary` — so either (a) `$onMultiR` isn't reaching all the redeclared symbols in lmp2 (maybe `Parameter` declarations with certain qualifiers escape), or (b) there's a second duplication path (not just `$include`) that bypasses `$onMultiR`. Needs a targeted lmp2 trace.

**Why batch them together?** Fixing #1275 doesn't fix #1281, but the diagnostic overhead of loading `_emit_nlp_presolve` is roughly the same for both. Lumping saves ~1h of re-onboarding.

**Caveat:** the original KU 2.3 expected the presolve emitter to live in `src/emit/original_symbols.py`. Actual site is `src/emit/emit_gams.py`. KU updated accordingly in §Verification below.

### 2.2 "Emitter idempotency" cluster (#1276, #1281)

**Shared structural pattern** (not shared code site):

- #1276: multiplier `.fx` emission for `nu_pbal` and `nu_qsb` is generated twice because two code paths (KKT classifier + emitter re-check) both conclude the multiplier should be fixed.
- #1281: `Parameter A(mm,nn)` declared twice because the emitter's regeneration pass and the `$include`-inlined source both declare it.

**Proposed shared helper:**

```python
class _DeclaredSymbolTracker:
    """Tracks (symbol_name, domain, condition) tuples already emitted in this output.

    Normalizes names case-insensitively (GAMS identifiers are case-insensitive)
    and skips redundant emissions within the same pass.
    """
    def __init__(self) -> None:
        self._seen: set[tuple[str, tuple[str, ...], str]] = set()
    def try_emit(self, name: str, domain: tuple[str, ...], condition: str) -> bool:
        key = (name.casefold(), domain, condition)
        if key in self._seen:
            return False
        self._seen.add(key)
        return True
```

Plumb through the multiplier-fixation emitter and the parameter-emission pass. Reduces two separate dedup fixes to one shared utility. Estimated savings: ~1h vs bespoke per-site fixes.

**Caveat on #1281 scope (KU 2.5):** the "inlined source" phrasing in ISSUE_1281 is technically imprecise — the actual mechanism is `$include` wrapped in `$onMultiR`/`$offMulti`, not literal inlining. `$onMultiR` is supposed to handle redeclarations, so the parse error may be from a narrower cause than "all Parameter declarations duplicated." Recommend running `gams <lmp2_mcp.gms> lo=2` during Sprint 25 to capture the exact error line before the fix begins.

### 2.3 Task 2 alias-AD cluster (#1277, #1278)

**#1277 connection to Task 2 §Section 3 Pattern C:**

- Pattern C's fix site (`_alias_match` in `src/ad/derivative_rules.py:304–307`) addresses the derivative chain's treatment of offset-alias pairs.
- `twocge_mcp.gms:497` (verified) shows `stat_tz` emitting `pq(j,r) * mu(j+1,r)` in the same offset group — both should be `pq(j+1,r) * mu(j+1,r)`, or both `pq(j,r) * mu(j,r)`, depending on the pairing. This is the post-derivative stationarity assembly step.
- Task 2's Sprint 24 inventory noted `_apply_alias_offset_to_deriv` (`src/kkt/stationarity.py:1743`) only rewrites `ParamRef` indices. twocge's bug shows a VarRef (`mu`) getting shifted while a sibling ParamRef (`pq`) doesn't — so the fix may need to extend the rewrite helper's target types AND respect a consistent offset-group contract.

**Status:** Partially subsumed. After Pattern C lands, re-run twocge; if `stat_tz` is still mixed, extend `_apply_alias_offset_to_deriv`. Budget 1–2h for this validation + targeted extension.

**#1278 distinct substitution bug:**

- Reproducer verified: `twocge_mcp.gms` lines 479, 482, 488 contain `$(ord(r) <> ord(r))` in `stat_e`, `stat_m`, `stat_pwe`. Original equations `eqpw` (line 559) and `eqw` (line 560) correctly use `$(ord(r) <> ord(rr))`.
- Code path: during instance enumeration in `src/kkt/stationarity.py`, when the differentiation substitutes `rr → concrete_rr_value` in the body, it ALSO substitutes the `$(ord(r) <> ord(rr))` guard's `rr` — collapsing the comparison to `ord(r) <> ord(r)`.
- Fix approach: preserve the summation-index name distinct from the bound-reference name in guards, or emit a fresh alias if name collision is unavoidable. Likely in `_apply_offset_substitution` or a sibling substitution pass (TBD — needs grep).
- **Task 2 alias-AD fix won't touch this path.** Separate 3–4h work item in Batch 3.

### 2.4 Standalone issues

- **#1279 (robustlp defobj)** lives in `src/ir/normalize.py` — the equation-domain inference step widens a scalar-body equation to the dominant set's index. Standalone fix; no shared code path with the emitter or AD clusters. 3–4h budget.
- **#1280 (unquoted UEL dots)** is a localized emitter-formatting fix (`_emit_uel` helper). No interaction with other issues. 1–2h budget.

---

## Section 3 — Proposed Batch Order

### Batch 1 — Days 1–2 (ship alongside Priority 1 Pattern A start)

| Issue | Effort | Why here |
|---|---|---|
| **#1275** (presolve absolute paths) | 2–3h | Single-line emitter bug, zero coupling to alias-AD. Shipping Day 1 makes every downstream `_presolve.gms` artifact portable for rest of sprint's regression runs. |
| **#1280** (unquoted UEL dots) | 1–2h | Localized emitter fix with clear test path. Mechanical change; no investigation risk. |

**Total Batch 1: 3–5h.** Can run in parallel to Priority 1 Day 1–2 Pattern A work without merge conflicts (different files).

### Batch 2 — Days 3–4

| Issue | Effort | Why here |
|---|---|---|
| **#1279** (robustlp defobj scalar-widening) | 3–4h | Standalone IR-normalize fix. Day 3 target because it's a high-severity potential recovery (robustlp `model_infeasible` → possibly `match`). |
| **#1276** (fawley duplicate `.fx`) | 1–2h | Introduces the `_DeclaredSymbolTracker` helper (see §2.2). First use site. |
| **#1281** (lmp2 duplicate Parameter) | 2–3h | Second use of `_DeclaredSymbolTracker`. Needs a GAMS `lo=2` compile trace first to confirm which declaration is the actual cause of `no_solve_summary`. |

**Total Batch 2: 6–9h.** The `_DeclaredSymbolTracker` helper should land once (in #1276's PR) and be reused by #1281.

### Batch 3 — Days 5–7 (after Pattern C lands in Priority 1)

| Issue | Effort | Why here |
|---|---|---|
| **#1277** (twocge `stat_tz` mixed offsets) | 1–2h | Post-Pattern-C verification; extend `_apply_alias_offset_to_deriv` if needed. Task 2 §Section 1 already flagged this extension as a stubbed item. |
| **#1278** (twocge `ord(r) <> ord(r)` tautology) | 3–4h | Independent substitution-preservation fix. Higher uncertainty — budget the full 4h. |

**Total Batch 3: 4–6h.** Gated on Pattern C landing; can be interleaved with the Pattern A→C rollout validation.

### Budget reconciliation

- Retrospective bound: 12–18h.
- This plan: 13–20h (with Batch 3's upper end slightly over; realistically 13–17h if Pattern C lands clean).
- **Parallelism opportunity:** Batches 1 and 2 fit within Days 1–4 with no dependencies on Priority 1's Pattern A work; Batch 3 is strictly gated on Pattern C. This lets the sprint lead dispatch Batch 1/2 to a separate contributor if available.

---

## Section 4 — Verification Artifacts

### Reproducers (verified 2026-04-20)

| Issue | Command | Expected Output |
|---|---|---|
| #1275 | `grep -n "^\$include" data/gamslib/mcp/robustlp_mcp_presolve.gms` | Absolute path starting with `/Users/jeff/...` |
| #1276 | `grep -cnE "^nu_(pbal\|qsb)\.fx" data/gamslib/mcp/fawley_mcp.gms` | 4 (expected: 2) — verified |
| #1277 | `grep -nE "^stat_tz.*mu\(j\+1.*pq\(j," data/gamslib/mcp/twocge_mcp.gms` | Mixed offsets on line 497 — verified |
| #1278 | `grep -n "ord(r) <> ord(r)" data/gamslib/mcp/twocge_mcp.gms` | 3 hits (lines 479, 482, 488) — verified |
| #1279 | `grep -n "^defobj(i)\.\." data/gamslib/mcp/robustlp_mcp.gms` | `defobj(i)` declared over i but body lacks i — verified |
| #1280 | `head -30 data/gamslib/mcp/mathopt4_mcp.gms \| grep "nlp2mcp_uel_registry"` | `x1.l, x1_0, x2.l, x2_0` unquoted — verified |
| #1281 | `grep -cnE "^Parameter\b" data/gamslib/mcp/lmp2_mcp.gms` | Current committed file shows 4 (no duplicates); pipeline status `path_solve_terminated` suggests the bug triggers on a regeneration path not captured in the current commit; Day 1 trace needed |

### Cross-check with Task 2 AUDIT

- Task 2 §Section 1 "Stubbed / Not Landed" row 3 (`_apply_alias_offset_to_deriv` multi-position extension) aligns with this catalog's §2.3 analysis of #1277.
- Task 2 §Section 1 "Stubbed" doesn't cover #1278's guard-substitution bug — this catalog adds it as a separate Sprint 25 fix site.

---

## Appendix A — Issue-to-PR Mapping (for PR12 regression fixture)

When implementing, each fix should land with:

1. **Unit test** under `tests/unit/emit/` or `tests/unit/kkt/` (per fix site)
2. **Regression assertion** on the affected model's MCP output (e.g., for #1276: "every `(multiplier, domain, condition)` tuple appears exactly once")
3. **Golden-file check** on any nearby matching models (from Task 2's canary ladder) to ensure no regression

For #1283's determinism fix (Task 3) landing alongside: `PYTHONHASHSEED` pinning should apply to ALL regression tests in Sprint 25, not just Task 3's specific cases. This is a shared-test-infrastructure item (PR12).
