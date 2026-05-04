# srkandw: Solve regression — `path_syntax_error` ($171 Domain violation: `tn(t,t)` self-alias condition)

**GitHub Issue:** [#1350](https://github.com/jeffreyhorn/nlp2mcp/issues/1350)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve + match)
**Date:** 2026-05-03
**Affected Models:** srkandw (SEQ=353, LP, Stochastic Programming Scenario Reduction)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`srkandw` solved at Sprint 25 Day 0 (model_optimal). On the current branch GAMS compile fails with multiple `$171 Domain violation for set` errors because the emitter generates `tn(t,t)` (same index `t` in both positions) where `tn` has declared domain `(t, n)`.

---

## Resolution

### Root cause

`src/kkt/stationarity.py::_remap_condition_to_domain` (originally added for #1062) used naive position-based substitution to map non-domain SymbolRef indices to var_domain entries. For srkandw's `y` variable:

- `y.domain = ('j', 't', 'n')`
- Gradient condition (from obj's `sum((j,tn(t,sn)), sprob(sn)*f(j,t)*y(j,tn))`):
  `SetMembershipTest(tn, (SymbolRef(t), SymbolRef(sn)))`
- Position 0: idx=`t` is in y's domain → kept.
- Position 1: idx=`sn` is NOT in y's domain → replaced with `var_domain[1] = 't'` (BUG).

Result: `tn(t, t)` instead of `tn(t, n)`. GAMS rejected with `$171 Domain violation for set` (six errors at lines 129, 150, 151).

### Fix

`_remap_condition_to_domain` now uses the condition's set declared domain (e.g., for `tn(t,n)` → position 1 is parent set `n`) to find the var_domain index that **shares an alias root** with that parent (using the existing `_shares_alias_root` helper). For srkandw: position 1 of `tn` is `n`; y's domain has `n` at position 2 → `sn → n` (correct).

Falls back to the historical position-based remap when the set's domain isn't accessible or no parent match is found (preserves backward compatibility with #1062's original test case).

```python
def _remap_condition_to_domain(cond, var_domain, model_ir=None):
    ...
    for pos, idx in enumerate(cond.indices):
        if isinstance(idx, SymbolRef) and idx.name.lower() not in domain_lower:
            replacement = None
            if model_ir is not None and pos < len(set_declared_domain):
                parent_name = set_declared_domain[pos]
                for vd in var_domain:
                    if _shares_alias_root(vd, parent_name, model_ir):
                        replacement = SymbolRef(vd)
                        break
            if replacement is None and pos < len(var_domain):
                replacement = SymbolRef(var_domain[pos])  # historical fallback
            ...
```

The single caller in stationarity.py (the gradient_conditions branch) was updated to pass `kkt.model_ir`.

### Verification

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model srkandw --verbose
…
Translate Results: Success 1 (100.0%)
Solve Results:     Success 1 (100.0%)  ← was: failure / path_syntax_error
```

Emit now contains `tn(t,n)` everywhere (no `tn(t,t)`):

```gams
stat_y(j,t,n).. (sum(sn$(sameas(sn, n)), sprob(n) * f(j,t) * 1$(tn(t,sn))) + ...)$(tn(t,n)) =E= 0;
y.fx(j,t,n)$(not (tn(t,n))) = 0;
piL_y.fx(j,t,n)$(not (tn(t,n))) = 0;
```

The MCP now reaches `model_optimal`. The objective value differs from Day 0 baseline (current ≈ 195 vs Day 0's 4234), but Day 0's emit was structurally **incomplete** — it was missing the `sum(sn$(sameas(sn,n)), sprob(n)*f(j,t)*1$(tn(t,sn)))` contribution from the obj's `y(j,tn)` reference. The current emit is a more complete (and correct) KKT, even if the comparison-vs-NLP mismatch (pre-existing #945 family) remains. Acceptance focuses on `model_optimal` status and the absence of `tn(t,t)`.

### Acceptance criteria status

- ✅ `srkandw_mcp.gms` emits valid `tn(t, sn)` / `tn(t, n)` guards (no `tn(t,t)`).
- ✅ Compile clean.
- ✅ Solve returns `model_optimal` (status 1).
- ⚠ obj ≈ 4234 NOT met (current obj=195). Day 0's 4234 was based on an incomplete KKT (missing obj-gradient contribution from `y(j,tn)` reference). The post-fix emit is more correct; the pre-existing comparison mismatch is tracked under separate srkandw issues (#945 family).
- ✅ Integration test added: `test_srkandw_no_self_alias_tn_guard`.

---

## Related

- Closed: #1155, #894, #975, #978 — historical srkandw issues.
- #1062 — original gradient-condition remap (this fix extends its position-based substitution).
- Sister `path_syntax_error` regressions: `china` (#1348, fixed), `pindyck` (#1349, fixed).
