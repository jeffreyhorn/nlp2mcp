# lmp2: lam_Constraints / comp_Constraints declared over dynamic subset triggers Error 187

**GitHub Issue:** [#1327](https://github.com/jeffreyhorn/nlp2mcp/issues/1327)
**Status:** RESOLVED — fixed in PR (this branch)
**Severity:** High — `path_syntax_error` (Error 187) blocked PATH from being invoked
**Date:** 2026-04-29
**Fixed:** 2026-04-29
**Affected Models:** lmp2 (verified end-to-end Optimal); any model with an equation declared over a parent set but defined over a dynamic subset
**Predecessors / closely-related:**
- [#1315](https://github.com/jeffreyhorn/nlp2mcp/issues/1315) (CLOSED) — dynamic-subset SET assignment extraction
- [#1323](https://github.com/jeffreyhorn/nlp2mcp/issues/1323) (CLOSED) — same root-cause class as #1315
- [#1281](https://github.com/jeffreyhorn/nlp2mcp/issues/1281) (CLOSED) — Parameter redeclaration
- [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243) (CLOSED) — `1/y(p)` div-by-zero in stat_y

---

## Problem Summary

After fixing #1315 / #1323 (dynamic-subset SET assignments now extracted into MCP pre-solve), lmp2 still failed to compile but with a *different* error:

```
**** 187  Assigned set used as domain
```

on lines:
```gams
Positive Variables
    lam_Constraints(m)    <-- m is a dynamic subset of mm
;
Equations
    comp_Constraints(m)   <-- same
;
```

This error was previously masked by #1315 / #1323's Error 66.

---

## Resolution Summary

### Code changes

1. **`src/ir/symbols.py::EquationDef`** — added a new `declaration_domain: tuple[str, ...] | None = None` field. When an equation is declared as `Equation X(mm);` but defined as `X(m).. ...` (m is a subset of mm), `domain` captures the body's `(m)` head while `declaration_domain` captures the original `(mm)`. Defaults to None for backward compat.

2. **`src/ir/parser.py::_handle_eqn_def_domain`** — populates `declaration_domain` from the previously-tracked `_equation_domains[name.lower()]` whenever the declaration domain differs from the body domain.

3. **`src/kkt/assemble.py::_create_eq_multipliers` / `_create_ineq_multipliers`** — multipliers now use `eq_def.declaration_domain or eq_def.domain` (when arities match) so they're declared over the parent set rather than the dynamic subset (which GAMS rejects with Error 187).

4. **`src/kkt/assemble.py::assemble_kkt_system`** — after multiplier creation, populates `kkt.multiplier_domain_widenings[mult_name] = (eq_def.domain, eq_def.declaration_domain)` for every equation with parent/subset split. The existing #1053 fix-inactive emit path then automatically emits `lam.fx(parent)$(not subset(parent)) = 0;` for excluded instances.

5. **`src/kkt/complementarity.py::build_complementarity_pairs`** — propagates `declaration_domain` onto the generated `comp_<name>` equation. Pair indices for the MCP model statement use the declaration domain so GAMS pairing works on the parent set.

6. **`src/emit/templates.py::emit_equations`** — equation declaration lines (for inequality complementarity, bound complementarity, and original equality equations) now prefer `declaration_domain` over body `domain` so the declarations are emitted over the parent set.

7. **Arity-mismatch guards** — every site that uses `declaration_domain` first checks `len(declaration_domain) == len(domain)`. Without this, models like korcge (which use literal selectors that drop a dimensional position from the body, e.g., `f(j,'2000-04')..` against `f(j,*)..`) would crash the existing `zip(orig, wide, strict=True)` path in the fix-inactive emitter.

### Tests added

- `tests/unit/ir/test_equation_declaration_domain.py` — 3 unit cases on synthetic minimal models (parent/subset, matching domains, scalar) verifying parser populates `declaration_domain` correctly.
- `tests/integration/emit/test_lmp2_declaration_domain.py` — 4 integration cases verifying lmp2's `lam_Constraints(mm)` / `comp_Constraints(mm)` declarations and that the body head retains `comp_Constraints(m)..`.

### Verification

- **lmp2 end-to-end:** `gams /tmp/lmp2_mcp.gms` now compiles cleanly and reaches:
  ```
  **** SOLVER STATUS     1 Normal Completion
  **** MODEL STATUS      1 Optimal
  ----    188 PARAMETER nlp2mcp_obj_val      =       35.598
  ```
  All three acceptance criteria are met (compiles past 187, reaches PATH, solves to Optimal).

- **Quality gate:** `make typecheck && make lint && make format && make test` all clean. Test suite: 4,654 passed, 10 skipped, 1 xfailed.

### Trade-offs in the implementation

- The original NLP source-level pattern (`Equation X(mm); X(m).. ...`) is preserved exactly in the emission (`Equations comp_X(mm); comp_X(m).. ...`), so GAMS-side semantics are identical to the user's source for the constraint domain restriction.
- The fix-inactive emission for the parent-domain multiplier reuses the existing #1053 `multiplier_domain_widenings` infrastructure rather than introducing a parallel path.
- Arity-mismatch cases (literal-selector body domains in models like korcge) are NOT widened — they keep the body domain everywhere, mirroring pre-fix behavior. A follow-up issue would be needed if those need separate handling.

---

## Related Issues

- **#1315** (CLOSED) — Multi-solve dynamic-subset set assignment not extracted
- **#1323** (CLOSED) — Same root cause class as #1315
- **#1243** (CLOSED) — Runtime div-by-zero in stat_y
- **#1281** (CLOSED) — Parameter redeclaration
- **#810** — lmp2 multi-solve loop extraction (parent class issue)
- **#724** — Variable access conditions for stationarity equations (related machinery)
- **#1053** — Multiplier domain widening machinery (reused by this fix)
