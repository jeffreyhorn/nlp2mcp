# ISSUE #1790 — emit: the NA-cleanup line is indexed by a parameter's repeated DECLARED domain, cleaning only the diagonal (Class B, gussrisk `covar`)

**GitHub:** [#1790](https://github.com/jeffreyhorn/nlp2mcp/issues/1790) · **Status:** 🟡 **IN PROGRESS** — Sprint 40 Day 8 (P4, the Class-B design; implemented because budget remained)
**Layer:** **emit**, `src/emit/original_symbols.py::emit_post_assignment_na_cleanup`

## Summary

**Class B (Sprint 40 P4): an emitted NA-cleanup line is indexed by a parameter's DECLARED domain.** When the declaration repeats a symbol, that touches only the diagonal.

gussrisk declares `covar(stocks,stocks)` and assigns `covar(s,sp) = sum(e, …)/card(e)` with `Alias (stocks,s,sp)`. The golden's cleanup is:

```
covar(stocks,stocks)$(NOT (covar(stocks,stocks) > -inf and covar(stocks,stocks) < inf)) = 0;
```

In GAMS a repeated controlling index is one iterator, so this cleans only `covar(i,i)`, while the assignment filled the full matrix. Off-diagonal `NA`/`UNDF` values would reach PATH's Jacobian (#1322's failure mode). It is P2's `covar(stocks,stocks)` baseline entry.

## The context is in the IR

`ParameterDef(domain=('stocks','stocks'), expressions=[(('s','sp'), <expr>)])` holds both the declaration and the assignment's LHS tuple (Prep Task 10 §3).

## Layer and design

**Emit**, `src/emit/original_symbols.py::emit_post_assignment_na_cleanup`. Index the cleanup by distinct per-position symbols:
1. the first assignment LHS whose indices are distinct set/alias names (`covar(s,sp)`);
2. else unused existing aliases of the repeated set;
3. else the declared domain, unchanged.

A domain without repeats is byte-identical.

## Not Class B

- shale's `ts(tf,tf)`: a stationarity guard; Class A, fixed by #1782.
- nonsharp's `inter(col,col,stm)` / `inter(col__kkt1,col__kkt1,stm)`: one reference of EACH class, in a MINLP the translator refuses (out of scope; regeneration cannot move it).

## Phase 0: Acceptance Gate (Sprint 40 Day 8, P4)

### Layer

**Emit**: `emit_post_assignment_na_cleanup` writes `name(<declared domain>)$(NOT (… > -inf and … < inf)) = 0;` from `ParameterDef.domain`. The IR, parser and AD layers are correct: the IR carries both the declaration and the assignment's LHS tuple.

### Nearest Existing Mechanism

**Nearest:** the parameter-assignment emitter, which already writes the assignment with its own LHS tuple (`covar(s,sp) = …`).

**Why it does not apply:** the NA cleanup is a separate pass. It reads only `param_def.domain`, never `expressions[k][0]`.

### Positive Control

A parameter whose declared domain has no repeated symbol (`p(i,k)`) emits its cleanup line byte-identically. Every NA-cleanup line in the corpus except gussrisk's must stay unchanged.

### Hand-Derived KKT Shape

Not a KKT change. **The target line** is `covar(s,sp)$(NOT (covar(s,sp) > -inf and covar(s,sp) < inf)) = 0;`, ranging over the full `stocks × stocks` matrix, as the assignment does.

### Expected Emit Pattern

- **gussrisk:** line 52 becomes `covar(s,sp)$(…) = 0;`, and P2 loses `gussrisk_mcp: covar(stocks,stocks)`.
- **No other golden changes.**

### Verification Methodology

1. **Fail-before / pass-after unit tests** (`tests/unit/emit/test_na_cleanup_repeated_domain.py`): the LHS case, the alias fallback, and a no-repeat control. The pre-fix emitter fails the first two.
2. `make check-index-repeats` (P2 ratchet), the full leak gate with `--resolve-changed`, then `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–2 hold, only gussrisk drifts, and its bucket holds.
- **REPLAN** on any other drift.

## PR #1791 review round 1

- An assignment LHS is accepted only when each index's alias chain resolves to the FULL declared set at that position (a subset LHS such as `p(s,j)` is not).
- The alias fallback reserves every declared name first (`p(i,i,j)` → `p(i,k,j)`).

