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

## PR #1783 review round 2: the same single position in EVERY reference

The binding requires the index at the same single position in every reference. A union let a fixed-cell reference independent of the index slip through: on `e(t).. 2*z('t3',t) - z('t2','t4')` it gave MCP 37.75 against NLP 7.5. The strict rule matches `main`. Mixed bound + independent references stay broken on every version; they are tracked on #1778.

## PR #1783 review round 3: the binding is applied ONCE

On `Alias(i,j,k)`, `z(i,j,k)`, `e(i,j).. z('a',i,j)` the binding `{0: 1, 1: 2}` is correct, and the dimension-mismatch branch already places the multiplier on the variable's coordinates (`nu_e(j,k)`). `_match_subset_domain` turned the same binding into the rename `{i: j, j: k}`, and `_rewrite_subset_to_superset` applied it a second time, giving `nu_e(k,k)`: a lost coordinate, and an MCP that did not solve (NLP 156).

**Fixed:** in `_match_subset_domain` the binding only SUPPRESSES a rename. It is accepted only when the bound position carries the mult index's own name; it never creates a rename. Every other case keeps `main`'s same-position / any-position matching. The offset-key pass is unchanged. The new emit is `nu_e(j,k)$(sameas(i,'a'))` and solves to 156. The #1782 fixture and the round 1–2 regressions are unchanged. spatequ's round-1 re-spelling (`nu_DX(rr,c)`) came from a binding-created rename, so it is undone: that golden is byte-identical to `main` again.


## Phase 0: Acceptance Gate (Sprint 40 Day 7, P4): turkpow `stat_ht`, the Pattern C binder

### Layer

**KKT / stationarity**: the Pattern C swap in `_add_indexed_jacobian_terms`. That is the gate `_find_pattern_c_alias_sum` and its consumer `_apply_pattern_c_swap_to_term`.
- **Measured on Day 7:** `pr(t).. sum(mt, … sum(v$vs(t,v), ht(mt,v)))` is a Pattern C shape. The gate fires (binder `v`, eq index `t`) and consolidates the offsets to zero. The matchers Day 6 fixed are NOT the layer here: an "absent from every reference" pass in `_compute_index_offset_key` left the row byte-identical.
- **The swap failed twice:**
  - **It is written for launch's naming.** `iweight(s)`, `sum(ss$ge(ss,s), …)`: the eq index name `s` is also the variable's position name. It exchanges binder ↔ EQ index. For `ht(m,v)` the binder IS the position name `v`, so the representative's labels and the binder both map to `v`, and the eq coordinate is lost before the swap runs: `vs(v,v) * lam_pr(v)`.
  - **It fires only on an all-zero offset key.** The dimension-mismatch key `(999, 0)` never reaches it, so `zh(m,b,t)` / `db(b,t).. sum(bp$bs(bp,b), zh(mh,bp,t))` keeps #1307's `sum(bp, bs(bp,b) * lam_db(b,t))`, a multiplier not indexed by the summed index.

### Nearest Existing Mechanism

**Nearest:** the launch swap itself (Sprint 26 Day 1 Phase A, restricted by #1398 to self-aliases). It is correct whenever the variable is declared over the eq index's name, and launch must stay byte-identical.

**Why it does not apply:** its swap pair is (binder, eq index). The invariant it relies on is (binder, **the variable position the binder occupies**), and the two coincide only under launch's naming.

**Also considered and rejected:** building the term from the source body, as B-1 does (`_build_plain_alias_consolidated_term`). B-1 is 1-D only. Generalising it means re-deriving the coefficient, guards and conditions outside the standard path, which is a much wider change.

### Positive Control

**The launch shape is unchanged:** `h(t)` (variable declared over the eq index's name), `pr(t).. sum(v$vs(t,v), h(v))` emits `sum(v, ((-1) * 1$(vs(v,t))) * lam_pr(v))` before and after. launch's golden must not drift.

### Hand-Derived KKT Shape

- `pr(t).. sum(m, a(m)·sum(v$vs(t,v), h(m,v))) ≥ …`: `∂ pr(t') / ∂ h(m,v) = a(m)·[vs(t',v)]` for EVERY `t'`. The eq index occupies no variable position.
- **Stationarity:** `… − sum(t', a(m)·vs(t',v)·lam_pr(t'))`. The eq index is summed, under a name the row's domain does not use.
- **shale's `cpu(m,t).. … =l= sum(tf$ts(t,tf), h(m,tf))`** with `t(tf)`: `… − sum(t'$t(t'), ts(t',tf)·lam_cpu(m,t'))`, which is Task 10 §2's hand-derived restored coupling.

### Expected Emit Pattern

- The swap pairs the binder with the variable position it occupies (the same single position in every reference, `_binder_var_position`), and only when the eq index is absent from every reference to the variable. A binder named like a variable position is first renamed to an alias of the same set that neither the variable nor the multiplier uses.
- **turkpow `stat_ht`:** `sum(t__kkt1, … vs(t__kkt1,v) … lam_pr(t__kkt1))$(t(t__kkt1))`. **P2: `vs(v,v)` gone.**
- **turkpow `stat_zh`:** `sum(bp, bs(b,bp) * lam_db(bp,t))`.
- **shale:** admitted through the gate as a subset ↔ parent pair (`t(tf)` with binder `tf`), only where the binder-position swap applies, never through the legacy offset-0 swap that #1398 restricted. **P2: `ts(tf,tf)` gone** (golden + presolve).
- **egypt (`tranc(rp,rp)`) is NOT this shape:** its two references hold the eq index at different positions (`trans(cf,rp,r) − trans(cf,r,rp)`), so the binder has no single position. It needs per-reference grouping and is carried to Day 8.

### Verification Methodology

1. **Fail-before / pass-after** on fixtures for each shape, each with its GAMS solve against the NLP optimum: binder named like the position (7.68), turkpow `ht` (0.0944), `zh` (112.264; `main` 558), shale `cpu` (9.9375; `main` 11.545).
2. The launch-shape positive control, byte-identical.
3. `make check-index-repeats`, ratchet **9 → ≤ 6** with `--update-baseline` in the same commit.
4. The full leak gate, with every drifted golden re-solved by `--resolve-changed`; then `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–4 hold and the resolver holds every bucket.
- **REPLAN** on any backward move, or if launch drifts.
- **egypt / shale stay MS 5:** expected (Task 10, necessary not sufficient). shale's candidate underlying defect is routed as **#1786** (a subset-defined equation sums over its bound subset index: `stat_z`).
