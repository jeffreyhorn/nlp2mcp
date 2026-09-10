# ISSUE #1737 — a repeated EQUATION domain silently collapses the index map

**GitHub:** [#1737](https://github.com/jeffreyhorn/nlp2mcp/issues/1737) · **Status:** 🟢 **GUARDED** (Sprint 39 Day 9) — latent defect, no corpus model triggers it
**Layer:** **IR / index binding** — `src/ir/index_map.py` (the guard), called from `src/kkt/empty_equation_detector.py` and `src/ir/condition_eval.py`
**Measured at:** `baa38562` · GAMS **54.2.1**

## Problem

`dict(zip(domain, values))` binds a domain's symbols to a concrete instance, and it is **silently wrong** when the domain repeats a symbol:

```python
dict(zip(("i", "i"), ("i1", "i2")))  ==  {"i": "i2"}
```

The first position is discarded with **no error**, so every downstream decision is made against half the tuple.

⚠ **`strict=True` does not catch this.** It compares *lengths*, which agree; the collapse happens in the `dict` construction afterwards. A reader seeing `strict=True` will reasonably assume the case is covered.

## Phase 0: Acceptance Gate

### Layer

`src/ir/index_map.py` — `assert_no_repeated_symbol` / `build_index_map`. Call sites: `src/kkt/empty_equation_detector.py` (per equation, hoisted out of the instance loop) and `src/ir/condition_eval.py` (per call).

### Nearest Existing Mechanism

**Nearest:** `dedupe_repeated_variable_domains` (`src/kkt/repeated_domain.py:51`, issue #1062), which rewrites repeated symbols in **variable** domains to fresh aliases before the AD layer.

**Why it does not apply here:**

1. **It covers variables only.** Measured from its AST: the sole rewrite loop is `list(model_ir.variables)` and the sole mutation target is `var_def.domain`. `model_ir.equations` appears **only** in its namespace-collision set, never after. These two call sites are **equation**-keyed.
2. **It is complete for what it does cover**, which is why the variable-keyed sites are *not* guarded: measured on all five models carrying the shape — `tricp` `slp(n,n)` → `(n, n__)`, `lop` `dtr(s,s,s,s)` → `(s, s__, s___, s____)`, `ferts` `xi(c,i,i)` → `(c, i, i__)` — **zero repeats remaining**. A local guard there would be dead code whose fail-before has nothing to fail on.
3. So the protection is **total for variables and absent for equations**. Extending #1062 to equation domains would be a different change: GAMS binds a repeated controlling index in an equation *definition* **diagonally**, so the correct handling is diagonal instance generation, not alias minting.

**Also considered and rejected:** `strict=True` on the existing `zip`, already present at both sites. It catches a length mismatch, not a key collapse.

### Hand-Derived KKT Shape

**Unchanged — and that is the acceptance criterion, not an omission.** This is a *defensive* change: it converts a silent wrong answer into a diagnosable failure. No stationarity row, multiplier, complementarity pair or bound may differ for any model that translates today.

The derivation is therefore **negative**: for every corpus model, ∂h/∂x and every emitted guard are identical before and after, because the guard's condition is **false for every model** — no corpus model declares a repeated equation domain (220-model scan).

### Expected Emit Pattern

**BYTE-IDENTICAL corpus-wide.** There is no new emitted construct. `make check-goldens` must report **186 checked, all clean, 0 drifted**; any drift is a failure.

On a model that *does* carry a repeated equation domain, the expected behaviour is **`RepeatedDomainSymbolError`**, naming the context and the repeated symbol — not a silently collapsed map.

### Verification Methodology

1. **Fail-before, at the defect itself.** Assert the collapse explicitly before asserting the guard, so the guard cannot later be read as redundant:
   `dict(zip(("i","i"),("i1","i2"))) == {"i": "i2"}` — then `build_index_map` raises on the same input.
2. **Shape coverage.** Case-insensitive (`("I","i")`), non-adjacent (`("i","j","i")`), triple (`("t","t","t")` → one dupe), multi-dupe (`("a","b","a","b")`). A distinct domain must bind normally.
3. **Emit invariance.** `make check-goldens` → **186 clean, 0 drift**, run **uncontended** (a contended run reports unverified timeouts and silently narrows scope).
4. **Corpus safety.** These are corpus-wide code paths: `condition_eval` is reached by every model with a conditioned equation. A leak here is not local.
5. **⚠ Scope, not just verdict.** State how many models could reach the guard (**0** today) alongside the pass, so a future reader can tell a real pass from an unexercised one.

### PROCEED/REPLAN Signal

**PROCEED** — `check-goldens` **186 clean, 0 drift**; the guard raises on every repeated-domain shape in §2 and on none of the distinct ones; full suite green.

**REPLAN** if any of:

- **any golden drifts.** A defensive change has no emit improvement to trade against; one drifted byte is a failed gate.
- **a corpus model reaches the raise.** Then the defect is *live*, not latent, and the correct fix is diagonal instance generation (GAMS's actual semantics) rather than refusal — a different and larger change.
- **the guard is reached in a per-instance loop.** It is validated once per equation by design; if a caller needs it per instance, the cost must be measured before accepting it.

### Bucket / KPI

**0 bucket, no KPI movement.** No model changes status: the guard is unreachable with current corpus data, which is precisely why it can land safely.
