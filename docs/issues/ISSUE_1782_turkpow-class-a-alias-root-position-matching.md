# ISSUE #1782 — turkpow Class A: an equation index matched to an aliased variable position by alias root

**GitHub:** [#1782](https://github.com/jeffreyhorn/nlp2mcp/issues/1782) · **Status:** 🟡 **IN PROGRESS** — Sprint 40 P4 (Day 6)
**Layer:** **KKT / stationarity** — the eq-index → variable-position matchers `_compute_index_offset_key` and `_match_subset_domain` (`src/kkt/stationarity.py`)


## Symptom

turkpow's committed `stat_zt(m,v,b,t)` carries `sum(t__kkt1, … opcostt(m,v,t__kkt1) * dur(b) * 1$(vs(t__kkt1,t__kkt1)) … * nu_ao(v))`. That is the P2 violations `vs(t__kkt1,t__kkt1)` / `vs(t__kkt2,t__kkt2)`, and the wrong multiplier `nu_ao(v)`. The correct term is `-opcostt(m,v,t)*dur(b)*nu_ao(t)$vs(t,v)`.

## Minimal reproducer

```gams
Set t / t1*t3 /;  Alias (t,v);
Set s(t,v);  s(t,v) = yes$(ord(t) <= ord(v));
Parameter c(t,v);  c(t,v) = 1 + ord(t) + 2*ord(v);
Variable z(v,t), obj;  Equation e(t), defobj;
e(t).. sum(v$s(t,v), c(v,t)*z(v,t)) =e= 1;
defobj.. obj =e= sum((v,t), sqr(z(v,t)));
```

- **Emitted on `main`:** `stat_z(v,t).. 2*z(v,t) + sum(t__kkt1, c(v,t__kkt1)*1$(s(t__kkt1,t__kkt1))*nu_e(v)) =E= 0;`. The MCP solves to **0.045** against an NLP of **0.0318**.
- **Correct:** `2*z(v,t) + c(v,t)*1$(s(t,v))*nu_e(t)`. The same model with DISTINCT sets (labels `v1*v3`) emits exactly this and solves to 0.026 = NLP.

## Mechanism (traced)

Two matchers pair the equation's index with a variable position by ALIAS ROOT. With `Alias(t,v)`, both of `z(v,t)`'s positions canonicalize to `t`, and each matcher takes position 0 (`v`), not the position literally named `t`:

1. `_compute_index_offset_key`'s canonical pass. The offset key then leaves the genuine `t` "unmatched", so the multiplier becomes `nu_e(v)`.
2. `_match_subset_domain`'s same-position preference. It returns the rename `{t: v}`, the mult index is treated as an independent iteration variable, minted as `t__kkt1` and summed over, and the AD's symbolic binder `v` (kept per #720/#1085) is then mapped to `t`, giving `s(t,t)`.

A third candidate, the alias-remap layer that the pre-trace observed producing `{'v': 't'}`, is downstream: fixing only the two matchers yields the correct row.

## Phase 0: Acceptance Gate (Sprint 40 Day 6, P4)

### Layer

**KKT / stationarity**: the two matchers that pair an equation's domain index with a variable position, `_compute_index_offset_key`'s canonical pass and `_match_subset_domain`'s same-position preference.
- The pre-trace (`CORRECTNESS_PRETRACES.md` §1) named "`_replace_indices_in_expr`'s alias ChainMap layer". **Day 6 refined that.** The `{'v': 't'}` alias remap it observed is a CONSEQUENCE of the matching: neutralizing it alone leaves the row correct when the matchers are fixed, and wrong when they are not. Measured: fix the alias layer only → still `nu_e(v)` / a minted sum; fix the matchers only → the correct row.
- **The `t__kkt1` mint is not patched.** It is downstream and correct for its input, as the pre-trace said.

### Nearest Existing Mechanism

**Nearest:** the matchers' own first passes. `_compute_index_offset_key` matches by canonical (alias-resolved) name, then by root. `_match_subset_domain` tries the same position first, "to avoid greedy first-match mapping to the wrong position" (its own comment).

**Why it does not apply:** both tie-breaks were written for SUBSETS and distinct-but-related sets. Under `Alias(t,v)` every position canonicalizes to the same root, so the canonical and same-position tie-breaks are **insufficient**: they cannot tell `v` from `t`. The only discriminator left is the **declared name**, and neither pass looks at it.

**Also considered and rejected:**
- **Reversing #1085**, i.e. substituting the concrete label for the collapsed binder, as the partial-collapse path does. This is wider: it changes every full-collapse condition corpus-wide. The pre-trace flagged it as the larger option.
- **Element-value matching:** the codebase moved away from it deliberately (#1099/#1100: shared labels in marco and markov).

### Positive Control

The same fixture with **distinct** sets (`Set v / v1*v3 /`, no `Alias`) already emits `c(v,t)*1$(s(t,v))*nu_e(t)` and solves to 0.026 = NLP. It must stay **byte-identical**.

### Hand-Derived KKT Shape

- `∂ e(t') / ∂ z(v,t) = c(v,t)·[s(t,v)]` if `t' = t`, else 0. The equation index IS the variable's second coordinate.
- **Stationarity:** `stat_z(v,t).. 2*z(v,t) + c(v,t)*1$(s(t,v))*nu_e(t) =E= 0`. There is no sum: nothing remains free.

### Expected Emit Pattern

- **Fixture:** exactly the hand-derived row (the positive control's form). P2 holds: no `$(…)` guard repeats a coordinate, and the multiplier is `nu_e(t)`.
- **turkpow:** `stat_zt` loses `vs(t__kkt1,t__kkt1)` / `vs(t__kkt2,t__kkt2)`, and the multiplier becomes `nu_ao(t)`. **P2 ratchet 11 → 9** with `--update-baseline` in the same commit. (The baseline was 9 at prep; 11 after Day 3's egypt/shale presolve copies.)
- **Corpus:** any golden that changes is a candidate instance, examined with the resolver.

### Verification Methodology

1. **Fail-before / pass-after** on the fixture: the row, the P2 property, and the GAMS solve (NLP 0.0318; `main` 0.045).
2. **The positive control** byte-identical.
3. **Necessity:** each matcher fix reverted on its own must break the fixture (measured: without the offset-key pass, `nu_e(v)`; without the subset-domain preference, a `t__kkt1` sum).
4. `make check-index-repeats`, the full leak gate (complete) with every drifted golden re-solved by `--resolve-changed`, then `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–4 hold and the resolver holds every bucket.
- **REPLAN** on any backward move.
- ⚠ **Bounded, not fixed here: turkpow's THIRD violation `vs(v,v)`** in `stat_ht(m,v)`. In `pr(t).. … sum(v$vs(t,v), ht(mt,v))` the equation index `t` has **no** counterpart in `ht(m,v)`, and the canonical pass still pairs it with `v`, its alias. The correct term sums over `t`: `sum(t$vs(t,v), …*lam_pr(t))`. The emit keeps only the diagonal.
  - The exact-name pass cannot reach this: no position is named `t`.
  - It needs a "position whose value IS the eq index" discriminator, i.e. a new design. **Carried to Day 7.** It also touches #1778's family: #1778's freej2 moves from 0.375 to 0.360 under this change, NLP 0.3333, so it is changed but not fixed.

## Phase 0 results (Sprint 40 Day 6): PROCEED for the `stat_zt` shape; the `stat_ht` shape is bounded

**The fix:** two exact-name preferences.
- `_compute_index_offset_key` gets a pass 0 that matches the variable position declared with the equation index's own name.
- `_match_subset_domain` tries that same-named position before the same-position preference.

**The alias-remap layer is NOT changed.** Measured unnecessary: with only the two matchers fixed, the row is correct.

| criterion | result |
|---|---|
| fail-before (`main`) | `sum(t__kkt1, c(v,t__kkt1)*1$(s(t__kkt1,t__kkt1))*nu_e(v))`, MCP 0.045 vs NLP 0.0318 |
| pass-after | `c(v,t)*1$(s(t,v))*nu_e(t)`, the hand-derived row; MCP **0.032** = NLP |
| positive control (distinct sets) | byte-identical |
| necessity | without the offset-key pass: `nu_e(v)`; without the subset-domain preference: a `t__kkt1` sum |
| P2 ratchet | **11 → 9**: turkpow's `vs(t__kkt1,t__kkt1)` and `vs(t__kkt2,t__kkt2)` are gone; `--update-baseline` in this commit |
| corpus (leak gate + resolver) | **5 goldens over 3 models drifted** (sambal, qsambal and their presolves; turkpow). **GO: all 3 held their bucket** |
| mutation controls | `main`: 4 tests fail; without the offset-key pass: 3; without the subset-domain preference: 4. The positive control passes in all |

**A pre-trace judgment corrected: sambal was not a correct positive control.** The pre-trace called sambal's minted emit correct. It was the same defect:
- the committed golden had `sum(i__kkt1, -1$(xb(i,i__kkt1)) * nu_cbal(i))`;
- `cbal(j).. t(j) =e= sum(i$xb(i,j), x(i,j))` gives `−1$(xb(i,j)) * nu_cbal(j)`, which is **the new emit**.

sambal and qsambal hold their **presolve** match. Their cold solves stay wrong (old 1028, new 781, NLP 3.97) for other reasons, so this corrects a term but moves no bucket.

**Bounded, carried to Day 7:** turkpow's `stat_ht` `vs(v,v)` (an eq index with no variable counterpart; see the PROCEED/REPLAN signal above). turkpow stays `path_syntax_error` for other reasons, unchanged.

## PR #1783 review round 1: the binding comes from the REFERENCE

- **The declared-name preference was replaced.** It broke a reversed equal-arity domain (`e(j,i).. x(j,i)`: `nu_e(j,i)`, wrong multiplier values) and a fixed-coordinate reference (`e(t).. z(t,'t1')`: the MCP did not solve).
- `_eq_index_ref_binding` reads, from the equation body, the variable position each equation index actually occupies. It binds only when there is exactly one such position across every reference; otherwise both matchers keep `main`'s logic.
- **The fixture, turkpow, sambal and qsambal are unchanged from the name-based result.**
- One extra golden (spatequ) re-spells a multiplier declaration over the alias `rr` (the same set); the resolver holds its bucket.
- **Note for Day 7:** the binding also says when an equation index occupies NO position, which is turkpow's `stat_ht` case. It is not used yet: the fallback is unchanged by design.
