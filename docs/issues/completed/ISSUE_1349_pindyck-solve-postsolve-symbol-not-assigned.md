# pindyck: Solve regression — `path_syntax_error` ($141 "Symbol declared but no values assigned" in post-solve `r.l(t) = r.l(t-1) - d.l(t)`)

**GitHub Issue:** [#1349](https://github.com/jeffreyhorn/nlp2mcp/issues/1349)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve + match)
**Date:** 2026-05-03
**Affected Models:** pindyck (SEQ=249, NLP, Optimal Pricing and Extraction for OPEC)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`pindyck` solved at Sprint 25 Day 0 (model_optimal, obj=1170.486, **matched**). On the current branch GAMS compile of the emitted MCP fails with $141 errors in the recurrence loop:

```
141   r.l(t) = r.l(t-1) - d.l(t)
                         $141
**** 141  Symbol declared but no values have been assigned.
```

---

## Resolution

### Root cause

The pindyck source has:

```gams
td.fx("1974") = 18;     ! sets td.lo = td.up = 18  AND  td.l = 18
s.fx ("1974") = 6.5;
r.fx ("1974") = 500;
cs.fx("1974") = 0.0;

loop(t$to(t), r.l(t) = r.l(t-1) - d.l(t));
```

GAMS's `var.fx(idx) = val` is shorthand that sets BOTH the bounds (`var.lo`, `var.up`) AND the level (`var.l`). The recurrence loop relies on the `.l` side effect — `r.l('1974')` must be 500 when the loop body computes `r.l('1975') = r.l('1974') - d.l('1975')`.

The MCP emitter replaces each `var.fx(idx) = val` with a complementarity equation `<var>_fx_<idx>.. <var>(idx) - val =E= 0` paired with a multiplier `nu_<var>_fx_<idx>` (so the constraint solver enforces the fix at solve time). When the equation is paired in the MCP, the `var.fx(idx) = val` line is suppressed (otherwise GAMS would hold-fix the column and leave the equation row empty — see #1234).

But the suppression dropped the `.l` side effect. The recurrence loop therefore ran with `r.l('1974') = NA` and aborted at compile time.

### Fix

`src/emit/emit_gams.py` — when the `_fx_` equation is paired in the MCP, also emit `var.l(idx) = val` so subsequent var-init recurrences have a populated initial value. The `.fx` assignment is still skipped (the equation handles the bounds via complementarity); only the `.l` side effect is preserved.

```python
if eq_paired_in_mcp:
    bound_lines.append(f"{var_name}.l({idx_str}) = {val_str};")
    continue
```

### Verification

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model pindyck --verbose
…
Translate Results: Success 1 (100.0%)
Solve Results:     Success 1 (100.0%)
Comparison Results: Match 1 (100.0%)
Full pipeline success: 1/1 (100.0%)
```

Emitted file now contains, before the recurrence loop:

```gams
td.l('1974') = 18;
s.l('1974') = 6.5;
cs.l('1974') = 0;
r.l('1974') = 500;
…
loop(t$to(t),
   r.l(t) = r.l(t-1) - d.l(t)
);
```

### Acceptance criteria status

- ✅ pindyck_mcp.gms compiles without $141.
- ✅ Solve returns `model_optimal` with obj ≈ 1170.486.
- ✅ Comparison match.
- ✅ Integration test added: `test_pindyck_emits_l_init_for_fx_equation_diagonal`.

---

## Related

- Closed: #1088, #893 — historical pindyck `.l`/loop ordering issues.
- #1234 — earlier fix that introduced the `.fx` suppression to avoid hold-fix/empty-equation conflicts. This fix preserves the `.l` half of the side effect that #1234 inadvertently dropped.
- Sister `path_syntax_error` regressions: `china` (#1348 — fixed via parser/ad subset handling), `srkandw` (#1350).
