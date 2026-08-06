# Sprint 36 — markov P1 Part-2 (`σ=sp`) Off-Diagonal Enumeration Design (Prep Task 3)

**Date:** 2026-08-06 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task3` · **Scope:** docs/analysis-only (src prototype reverted; branch byte-identical to `main`).
**Outcome: the `σ=sp` representation gap is precisely root-caused, a bounded (additive, gated) mechanism is specified with two alternatives, and the Phase-0 `CASE_A` control + the leak-freedom gate are defined. Go/no-go: GO with a REPLAN exit — Part-2 is landable but is the deepest single change in P1 (a coordinated offset-key + emission change), so it front-loads Days 1–3 with "ship Part-1 + bank Part-2" as the exit.** Verifies Unknowns 1.2, 1.3, 1.4.

Reference: `DAY11_MARKOV_DIAGONAL_LEVER.md` §2–§6 (the diagnosis + Part-1 verified 13.3→1.55); `DAY0_TRACE_NOTES.md` (the fingerprints re-confirm). Code: `src/kkt/stationarity.py` — `_compute_index_offset_key` (`:4969`), the offset-grouping + emission in `_add_indexed_jacobian_terms` (`:5861+`).

---

## 1. The representation gap — root-caused (Unknown 1.2)

markov's stationarity: `constr(sp,j).. sum(spp, z(sp,j,spp)) − b·sum((s,i,spp), pi(s,i,sp,j,spp)·z(s,i,spp)) =e= beta`. `pi(s,i,sp,j,spp) = pr(i,j)` **only when `spp = sp`** (from the assignment `pi(s,i,sp,j,sp)=pr(i,j)`). Hand-deriving `∂constr(σ,τ)/∂z(s,i,sp)`:
```
∂constr(σ,τ)/∂z(s,i,sp) = [σ=s][τ=i]  −  b·pi(s,i,σ,τ,sp) ,   and  pi(s,i,σ,τ,sp) = pr(i,τ)  iff  σ = sp
```
So the off-diagonal contribution's constraint index is **`σ = sp`** — the variable's *3rd, independent* index (not the 1st, `s`).

**Why the emitter cannot represent it (confirmed by instrumentation, this task):** `_compute_index_offset_key` (the #1045/#1086 dimension-mismatch path, `:5038+`) matches each **constraint** domain index to a **variable** position by a **greedy first-canonical-match** (`:5099–5104`):
```python
for ei in range(len(eq_domain)):            # eq_domain = ('sp','j')  (constr)
    for vi in range(len(var_domain)):        # var_domain = ('s','i','sp')  (z)
        if vi not in used_var and eq_canons[ei] == var_canons[vi]:
            offsets_list[vi] = _compute_offset_at(ei, vi); used_var.add(vi); break
```
Because `s`, `sp`, `spp` are **aliases** (same canonical set), `eq_canons = [canon(sp)=s, canon(j)=i]` and `var_canons = [s, i, s]`. For the constraint's first index `sp` (`ei=0`, canon `s`) the loop **binds it to var position 0 (`s`)** — the *first* position sharing canon `s` — and never reaches position 2 (`sp`). The actual `σ=sp` value is then expressed as an **offset from `s`**: `offset = pos(sp) − pos(s)`, which varies over every `(s,sp)` pair.

**Empirical confirmation (instrumented emit, reverted):**
```
[OD] eq=constr var=z mult_domain=('sp','j') var_domain=('s','i','sp') ngroups=45
[OD] diagonal keys (all-0/sentinel): [(0, 0, 999)]
[OD] 44 off-diagonal offset keys: (-7..+7, {-1,0,1}, 999)   ← σ as offset-from-s at pos 0; pos 2 (sp) = SENTINEL
[OD] sample: eq_idx(σ,τ)=('12','normal') var_idx(s,i,sp)=('12','disrupted','12')  ← σ bound to pos 0 (s), not pos 2 (sp)
```
The 8-element reserve set `s` gives σ-offsets from −7 to +7 → **44 spurious off-diagonal groups**, each emitting `sum((s__kktN,j), (−b·pi(…s__kktN…))·nu_constr(s__kktN, j±k))$(ord()/sameas guards)`.

**Contrast — the sibling `equil(s,spp)` binds correctly:** its first index is `s` (canon `s`) → pos 0, and its second `spp` (canon `s`) → pos 2 (pos 0 taken) → a **single** group `(0,999,0)`. So the bug is specific: **a constraint index whose declared name matches a *later* var position (`sp↔sp`) but whose canon matches an *earlier* one (`sp↔s`) is greedily mis-bound to the earlier position.**

## 2. The correct target form

With `σ` correctly bound to the variable's `sp` (position 2), the off-diagonal collapses to a **single sum over `τ=j` only**:
```
stat_z(s,i,sp)  =  c(s,sp,i)
                +  nu_constr(s,i)                                   [Kronecker diagonal — direct]
                −  b · sum(j, pi(s,i,sp,j,sp) · nu_constr(sp,j))    [off-diagonal — σ=sp fixed, j summed]
                +  <equil terms>  −  piL_z(s,i,sp)
```
i.e. `nu_constr` indexed by **`(sp, j)`** (the variable's own `sp` + the summed `j`), replacing the 44 offset-from-`s` groups with one clean sum.

**Diagonal/off-diagonal reconciliation (the arbiter is the Phase-0 control).** The `(σ=s,τ=i)` entry lives in Part-1's diagonal group. Two consistent splits:
- **(a) [recommended] Kronecker-only diagonal + full off-diagonal:** Part-1 emits just `+ nu_constr(s,i)` (the Kronecker), and the off-diagonal `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` covers **all** `σ=sp` entries (including the `sp=s,j=i` self term). This matches the `test_markov_stationarity_has_correction_term` docstring's intended shape and has no double-count.
- **(b) Fused diagonal + excluded off-diagonal:** Part-1 keeps the verified `(1 − b·pi(s,i,s,i,sp))·nu_constr(s,i)`, and the off-diagonal excludes the diagonal cell via `$(not (sameas(sp,s) and sameas(j,i)))`.

Both are algebraically equal; **(a) is cleaner** (no exclusion guard) but re-scopes Part-1 from the fused form (verified 13.3→1.55) to Kronecker-only. The Phase-0 `/tmp` control (§5) picks whichever reaches `CASE_A` on the emitted golden.

## 3. Candidate mechanisms (with blast radius)

**Prototype finding (this task):** changing *only* `_compute_index_offset_key` (an exact-declared-name-first pass so `sp`→var pos 2) left `ngroups=45` unchanged **and crashed the emission** — because the downstream sub-group emission (`:6136+`, the #1104 fresh-alias sum) is not prepared to build `nu_constr(sp,τ)` from a position-2-bound key. **⇒ Part-2 is inherently a coordinated offset-key + emission change, not a one-line tweak** (confirming DAY11's "substantial rewrite" assessment).

### Mechanism C — targeted additive off-diagonal correction (RECOMMENDED, lowest blast radius)
Mirror the **working Part-1** approach (`_kronecker_diag_correction` + `_skip_summed_term`): detect the "constraint index bound to an independent non-first var index" signature and (1) **suppress** the 44 spurious offset groups for that variable, (2) **append** a single direct correction `− b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` built with `σ` substituted by the var's `sp`.
- **Signature gate (tight):** a `mult_domain` index whose alias-canon matches ≥ 2 `var_domain` positions, where a *later* position is an exact declared-name match (`sp`↔`sp`) and an *earlier* one is canon-only (`sp`↔`s`). markov's `constr` fires; `equil` does not (it has no name-vs-canon split); the 2-D cohort does not (no aliased-index-in-later-position — to be confirmed by the leak gate, §6).
- **Emitted GAMS:** `... + nu_constr(s,i)$(…) - sum(j, (b*pi(s,i,sp,j,sp))*nu_constr(sp,j)) + <equil> ...` (one sum, replacing the 44 groups).
- **Blast radius: LOW** — additive + gated, parallel to Part-1; does **not** touch the shared `_compute_index_offset_key` matcher used by every dimension-mismatch model.

### Mechanism A — fix the offset-key matcher (exact-name-first) + coordinate the emission (root fix, higher risk)
Add an exact-declared-name pass before the canon pass in `_compute_index_offset_key` (so `sp`→pos 2, offset 0), collapsing the 44 groups into one, **and** update the sub-group emission to build `nu_constr(sp,τ)` from a non-first-position binding.
- **Blast radius: HIGH** — `_compute_index_offset_key` is shared by *all* dimension-mismatch models (the 2-D cohort + every aliased model); re-ordering the match could silently re-group cohort entries. The prototype showed the emission must change in lockstep. This is the "correct general fix" but the riskiest.

### Mechanism B — an explicit "bound-to-var-index" offset-key marker (middle ground)
Introduce a marker distinct from `_SENTINEL_UNMATCHED` meaning "this constraint index is bound by value to var position N": the key becomes `(BOUND→2, offset(τ,i), 0)`; the emission consumes the marker to build `nu_constr(sp,τ)`. Fires only on the collision case.
- **Blast radius: MODERATE** — additive to the offset-key vocabulary + a new emission branch; gated on the collision, but still edits the shared computation.

## 4. Recommendation + code surface

**Adopt Mechanism C.** It reuses the verified Part-1 pattern (additive + gated correction; `DAY11_MARKOV_DIAGONAL_LEVER.md` §6 `_kronecker_diag_correction`), keeps the shared `_compute_index_offset_key` matcher **untouched** (the whole cohort-leak surface), and localizes the change to the same `_add_indexed_jacobian_terms` region Part-1 already modifies.

**Code surface (all in `src/kkt/stationarity.py`, `_add_indexed_jacobian_terms`):**
1. A signature detector `_independent_index_offdiagonal(...)` (mult index canon-matches ≥2 var positions with a later exact-name position) — computed alongside the Part-1 `_mult_var_collision`/`_all_zero_offset` gate.
2. When it fires: set `_offdiag_independent_correction = Binary("-", 0, Sum((τ,), Binary("*", b·pi(s,i,sp,τ,sp), MultiplierRef(mult_base, (sp, τ)))))` and suppress the offset-group loop's spurious terms for this variable (a `_skip_offdiag_groups` flag, mirroring Part-1's `_skip_summed_term`).
3. Append `_offdiag_independent_correction` next to the Part-1 `_kronecker_diag_correction` append (`:7218` region), using reconciliation (a) — Part-1 emits the Kronecker-only diagonal.

## 5. Phase-0 `CASE_A` control (must pass before any `src/`) — Unknown 1.4

**Gate:** hand-edit the emitted `markov_mcp.gms` `stat_z` to the §2 target form (Part-1 Kronecker-only diagonal + the single `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` off-diagonal, replacing the 44 groups), then run the KKT-residual harness — it **must** reach `CASE_A` (rel < tol) and, cold-solved, `model_optimal`.
- markov is tiny (2 vars / 3 eqns / 212-line MCP) ⇒ each control iteration is seconds-scale and fully **local** (no testbed gate). This is why markov is the sprint's strongest, lowest-cost lever.
- The control also **arbitrates the reconciliation** (§2 (a) vs (b)): try (a) first; if a residual remains at the `sp=s,j=i` cell, apply (b)'s exclusion guard.
- **Unknown 1.4 (methodology→genuine):** markov is `verified_convex` + currently `model_optimal_presolve` + match (methodology; re-confirmed Task 2). A `CASE_A` cold emit ⇒ the cold MCP solves `model_optimal` ⇒ genuine match ⇒ **genuine floor 75→76 (+1)**. The Phase-0 cold-solve is the direct confirmation (local, cheap).

## 6. Leak-freedom gate (2-D cohort) — Unknown 1.3

**Gate:** after the `src/` change, `check_golden_staleness.py` (or a targeted cohort emit-diff) must show **only markov drifts** — cesam2 / camcge / ps2_f_s / ps2_s / ps3_s_gic / polygon **byte-identical**. Mechanism C is leak-free *by construction* (additive + gated on the markov-specific `σ=sp` signature; it does not touch `_compute_index_offset_key`), but the empirical golden-staleness run is the confirmation.
- **Cost caveat (from DAY11):** the 2-D cohort emits are minutes-scale (timed out at a 100 s cap on Day 11). Plan the leak gate as either a nightly/async run or a per-model targeted diff, not an inline `make test` step.
- **Interaction with the fawley Task-4 discriminator:** both Part-2 (markov) and the fawley discriminator are additive, gated branches in `_add_indexed_jacobian_terms` — Task 4 produces the joint change-surface map proving non-overlapping firing conditions (markov's `σ=sp` independent-index signature vs fawley's constraint-index-diagonal `sameas` signature).

## 7. Go / No-Go + REPLAN exit

**GO** — Part-2 is landable: the root cause is precise, the target form is derived, Mechanism C is bounded (additive + gated, reusing the verified Part-1 pattern), and the Phase-0 `CASE_A` control is local + cheap. But it is the **deepest single change in P1** (a coordinated suppress-groups + emit-correction change), so:
- **Front-load Days 1–3** (markov is the strongest, fully-local +1 — worth the earliest budget).
- **REPLAN exit:** if the Phase-0 `/tmp` control cannot reach `CASE_A` with a bounded correction, OR the golden-staleness gate shows a cohort leak, **ship Part-1 (Kronecker split — correctness-only, no bucket) and bank Part-2** with this sharpened spec + the `/tmp` control result. Part-1 alone is a safe, verified correctness improvement; the +1 floor is Part-2-contingent.
- **Budget fit:** Mechanism C is within the P1 14–20h budget (Part-1 is done; Part-2 = the detector + the correction + the control + the leak gate). Mechanism A/B would exceed it (shared-matcher rewrite + full cohort re-validation) — reserved as fallbacks only if C's gate leaks.

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 3 (markov Part-2 `σ=sp` design; GO with REPLAN exit)
**Last Updated:** 2026-08-06
**Owner:** Sprint 36 Execution Team
