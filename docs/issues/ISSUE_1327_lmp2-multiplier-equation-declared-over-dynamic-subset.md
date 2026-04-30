# lmp2: lam_Constraints / comp_Constraints declared over dynamic subset triggers Error 187

**GitHub Issue:** [#1327](https://github.com/jeffreyhorn/nlp2mcp/issues/1327)
**Status:** OPEN
**Severity:** High — `path_syntax_error` (Error 187) blocks PATH from being invoked
**Date:** 2026-04-29
**Affected Models:** lmp2 (observed); any model with an equation declared over a parent set but defined over a dynamic subset
**Predecessors / closely-related:**
- [#1315](https://github.com/jeffreyhorn/nlp2mcp/issues/1315) (CLOSED, fixed in PR #1328) — dynamic-subset SET assignment extraction
- [#1323](https://github.com/jeffreyhorn/nlp2mcp/issues/1323) (CLOSED, fixed in PR #1328) — same root-cause class as #1315
- [#1281](https://github.com/jeffreyhorn/nlp2mcp/issues/1281) (CLOSED, fixed in PR #1314) — Parameter redeclaration
- [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243) (CLOSED, fixed in PR #1328) — `1/y(p)` div-by-zero in stat_y

---

## Problem Summary

After fixing #1315 / #1323 (dynamic-subset SET assignments now extracted into MCP pre-solve), lmp2 still fails to compile but with a *different* error:

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

This error was previously masked by #1315 / #1323's Error 66 (`symbol "m" has no values assigned`). Once that compile-time blocker was removed in PR #1328, #1327 surfaced.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: FAIL (Error 187 — `Assigned set used as domain`)
- **PATH solve**: NOT INVOKED (compile error)
- **Pipeline category**: `path_syntax_error`
- **Predecessors fixed**: #1281 (PR #1314), #1243 / #1315 / #1323 (PR #1328)

---

## Reproduction (verified 2026-04-29 with PR #1328 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms \
    -o /tmp/lmp2_mcp.gms --quiet
cd /tmp && gams lmp2_mcp.gms lo=0

# Expected output:
# ****                      $187
# **** 187  Assigned set used as domain
# (on `lam_Constraints(m)` and `comp_Constraints(m)`)
```

Inspect the offending declarations:

```bash
grep -nE "lam_Constraints|comp_Constraints" /tmp/lmp2_mcp.gms | head -5
# 92:    lam_Constraints(m)         <-- m is dynamic subset, GAMS rejects
# 119:    comp_Constraints(m)       <-- same
# 134:stat_x(nn).. ... sum(m, A(m,nn) * lam_Constraints(m)) ...
# 138:comp_Constraints(m).. ((-1) * (b(m) - sum(n, A(m,n) * x(n)))) =G= 0;
# 174:    comp_Constraints.lam_Constraints,
```

---

## Root Cause

The original NLP source has:

```gams
Equation
   Objective
   Constraints(mm)        <-- declared over parent set mm
   Products(p);

Constraints(m).. b(m) =l= sum(n, A(m,n)*x(n));   <-- defined over dynamic subset m
```

This is a common GAMS pattern: **declare over parent set, define over dynamic subset**. GAMS validates that the subset is a subset of the parent at solve time. The body executes for the populated members of `m` only.

The IR parser stores `Constraints` with `domain = ('m',)` (taken from the body's `(m)` head), not `('mm',)` (from the declaration). The KKT pipeline then propagates this dynamic-subset domain to:

1. The multiplier `lam_Constraints` — declared as `Positive Variables lam_Constraints(m);`
2. The complementarity equation `comp_Constraints` — declared as `Equations comp_Constraints(m);`

But GAMS does not allow dynamic subsets as **declaration** domains — only as **iteration** domains in equation bodies.

```python
# In src/ir/parser.py (approximately):
# Equation parsing currently uses the body's `(m)` head, not the declaration's `(mm)`.
# IR field: EquationDef.domain = ('m',)
```

This is verified to be pre-existing behavior — the same `(m)` domain appeared in pre-#1315/#1323 emissions, but Error 66 fired earlier and masked the Error 187. After PR #1328 unmasks it, the issue surfaces.

---

## Expected Emission

```gams
Positive Variables
    lam_Constraints(mm)            <-- parent set
;
Equations
    comp_Constraints(mm)           <-- parent set
;

* Fix excluded instances
lam_Constraints.fx(mm)$(not m(mm)) = 0;

* Equation body conditioned on subset membership
comp_Constraints(mm)$(m(mm))..
    ((-1) * (b(mm) - sum(n, A(mm,n) * x(n)))) =G= 0;

* Stationarity equation: sum should iterate over parent set with subset filter
stat_x(nn).. (... + sum(mm$(m(mm)), ((-1) * A(mm,nn)) * lam_Constraints(mm)) - piL_x(nn))$(n(nn)) =E= 0;
```

This pattern (declare over parent, condition on subset) is already supported elsewhere in the emitter for similar cases (e.g., the lead/lag fix-inactive path, the `stationarity_conditions` machinery in #724).

---

## Fix Approach (RECOMMENDED)

Two layers need updating:

### Layer 1 — Track the equation's *declaration* domain separately from the body domain

In the IR (`src/ir/symbols.py::EquationDef`), add a `declaration_domain` field that captures the original `Equation Constraints(mm);` domain. The existing `domain` field continues to capture the body's `(m)` head. The parser populates both.

### Layer 2 — KKT pipeline uses declaration domain when generating multipliers / complementarity equations

In `src/kkt/multipliers.py` (and/or `src/kkt/complementarity.py`):
- Use `declaration_domain` for the multiplier's declared domain.
- Use `declaration_domain` for the complementarity equation's declared domain.
- Add a `$(subset(d))` body condition where `subset` is the dynamic-subset name from `domain`.
- Emit `multiplier.fx(d)$(not subset(d)) = 0;` to fix excluded instances.

For lmp2:
- `lam_Constraints` declaration: `Positive Variables lam_Constraints(mm);`
- `comp_Constraints` declaration: `Equations comp_Constraints(mm);`
- `comp_Constraints` body: `comp_Constraints(mm)$(m(mm)).. ... =G= 0;`
- Fix-inactive: `lam_Constraints.fx(mm)$(not m(mm)) = 0;`
- Stationarity sum: `stat_x(nn).. (... + sum(mm$(m(mm)), ...) ...)$(n(nn)) =E= 0;`

### Alternative — Always emit `m(mm) = yes;` to widen the dynamic subset

Less invasive but semantically incorrect (would make all parent-set elements active when only a subset is intended). The cases where this matters: any equation body that uses dynamic-subset filtering depends on `m`'s actual membership being a strict subset. In lmp2 it does — `Constraints(m)` is meant to apply only to the cases-determined subset.

Not recommended.

---

## Files Involved

- `src/ir/parser.py` — equation parsing (records body domain, drops declaration domain).
- `src/ir/symbols.py::EquationDef` — needs new `declaration_domain` field.
- `src/kkt/multipliers.py` — multiplier creation, currently uses `EquationDef.domain` for declared domain.
- `src/kkt/complementarity.py` — complementarity equation generation, same.
- `src/kkt/stationarity.py` — uses dynamic subset in `sum()` body without conditional filter.
- `src/emit/emit_gams.py` — emission of multiplier / equation declarations.
- `data/gamslib/raw/lmp2.gms` — primary repro corpus.

---

## Estimated Effort

5–8 hours:
- 1h: add `declaration_domain` field to `EquationDef` and populate from parser
- 2h: update KKT multiplier / complementarity / stationarity codepaths to use declaration domain + subset condition
- 2h: integration tests on lmp2 + a synthetic minimal repro
- 1h: corpus regression sweep on solve-success canary
- 1–2h: code review + fixes

---

## Acceptance Criterion

1. `gams /tmp/lmp2_mcp.gms` compiles cleanly past Error 187 (no Error 187 on `lam_Constraints` / `comp_Constraints`).
2. lmp2 reaches PATH-solve invocation.
3. Stretch: PATH solves to optimal and matches the NLP reference (still subject to non-convex local-optimum question).

---

## Related Issues

- **#1315** (CLOSED, fixed in PR #1328) — Multi-solve dynamic-subset set assignment not extracted
- **#1323** (CLOSED, fixed in PR #1328) — Same root cause class as #1315; this issue is the next-in-line residual after #1315/#1323
- **#1243** (CLOSED, fixed in PR #1328) — Runtime div-by-zero in stat_y (independent — different fix path, but same target model)
- **#1281** (CLOSED, fixed in PR #1314) — Parameter redeclaration
- **#810** — lmp2 multi-solve loop extraction (parent class issue)
- **#724** — Variable access conditions for stationarity equations (related machinery for KKT-side $-conditions)
