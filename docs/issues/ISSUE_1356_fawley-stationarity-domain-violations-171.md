# fawley: PATH $171 Domain Violations in Stationarity (Post-#1276 Fix Bucket Transfer)

**GitHub Issue:** [#1356](https://github.com/jeffreyhorn/nlp2mcp/issues/1356)
**Status:** OPEN — Sprint 26 carryforward (filed Sprint 25 Day 13)
**Severity:** Medium — model translates cleanly post-Sprint-25 fixes but PATH compilation fails with 3 `$171` errors
**Date:** 2026-05-05
**Last Updated:** 2026-05-27 (Sprint 27 Prep Task 2 — Phase 0 acceptance-gate section authored per PR20 codification)
**Affected Models:** fawley (confirmed); root cause not yet localized — may share family with #1357 (otpop)

---

## Problem Summary

After Sprint 25 closed #1276 (duplicate `.fx` emission), #1133 (empty mbal SetMembershipTest), and #1130 (table column alignment), the Day 11 retest shows fawley moved from `model_infeasible` to **`path_syntax_error`** — the emitted MCP now fails GAMS compilation with **3 `$171`** ("Domain violation for set") errors plus a downstream `$141`.

One of the four bucket additions during Sprint 25 (see SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation").

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/fawley.gms \
  -o /tmp/fawley_mcp.gms --skip-convexity-check --quiet
gams /tmp/fawley_mcp.gms lo=2

# *** Error 171 in /tmp/fawley_mcp.gms (line 273 ×2, line 315)
# *** Error 257 (cascade)
# *** Error 141 in /tmp/fawley_mcp.gms (line 381)
# *** Status: Compilation error(s)
```

---

## Diagnostic

GAMS error `$171` means a stationarity equation references a variable / parameter at an index outside the declared domain. Possible mechanisms:

1. `nu_<eq>(i)` with `i` taken from a superset (subset/superset domain confusion — same shape as the otpop issue #1175 that closed earlier).
2. An IndexOffset (`i+N`) that lands outside the multiplier's declared subset domain.
3. Aliased index mis-binding in the stationarity assembly path.

Without a deeper inspection of lines 273 / 315 of the emitted `fawley_mcp.gms` and a hand-trace back to which source equation produced them, the root cause is not yet localized — Sprint 26 should start with the `.lst`-line cross-reference.

---

## Where to Investigate (Sprint 26 Day 0 / 1)

1. Open `/tmp/fawley_mcp.gms` (regenerate per "Reproduction" above) and inspect lines 273 and 315.
2. Match each violating reference back to its source equation in `data/gamslib/raw/fawley.gms`.
3. Determine whether the violation is:
   - **Pattern C variant** (likely shared with #1354 / #1355 — phantom IndexOffset onto a multiplier's subset domain).
   - **Subset-superset confusion** (similar to closed #1175 otpop, which was Sprint 23/24 work — may indicate a regression).
   - **Domain-widening misalignment** (the multiplier's `declaration_domain` machinery from #1327 may be misaligned for fawley).

---

## Tests to Add

- **Integration test** in `tests/integration/emit/`: assert fawley's emitted MCP compiles cleanly under GAMS `lo=2` (or, more narrowly, asserts no `$171` substring in the `.lst` file). Currently no such regression test exists.
- Once root cause is identified, add a unit test in `tests/unit/kkt/` against the specific stationarity assembly path.

---

## Files Involved (preliminary — pending Sprint 26 root-cause)

- `src/kkt/stationarity.py` — likely
- `src/kkt/complementarity.py` — possible (if `multiplier_domain_widenings` arity mismatch)
- `data/gamslib/raw/fawley.gms` — source
- `data/gamslib/mcp/fawley_mcp.gms` — current buggy emit

---

## Estimated Effort

**4–8h** for diagnosis (line-by-line cross-reference + minimal repro extraction), then variable depending on root cause:
- If shared with **#1354 / #1355** (Pattern C variant): subsumed by that fix.
- If new: standalone ~6–10h.

---

## Related

- **#1276** (duplicate fx emission — CLOSED Sprint 25)
- **#1130** (table column alignment — CLOSED earlier)
- **#1133** (empty mbal SetMembershipTest — CLOSED earlier)
- **#1175** (otpop subset-superset domain violation — CLOSED; same `$171` shape, predecessor)
- **#1354 / #1355** (camcge / cesam2 phantom IndexOffset — possible shared Pattern C variant)
- **#1357** (otpop `$171` — also in the four-bucket-additions cohort; possibly same root cause)

---

## Phase 0: Acceptance Gate

**Authored:** 2026-05-27 (Sprint 27 Prep Task 2 per PR20 codification)
**Target equation(s):** `comp_up_u(c)$(cr(c) and crdat(c,"supply") < inf)` + `piU_u.fx(c)$(not (cr(c) and crdat(c,"supply") < inf))` at `data/gamslib/mcp/fawley_mcp.gms:273` and `:315`
**Bug class:** comp_up subset/superset domain widening — the upper-bound complementarity equation is declared over the superset `c` (all crudes) but the bound-defining parameter `crdat(c,"supply")` is declared over the subset `cr(c)` (refinable crudes only). GAMS evaluates the `crdat(c,"supply") < inf` predicate at compile-time across ALL `c` values, triggering `$171` ("Domain violation for set") at each `c` outside `cr`.

### Hand-Derived KKT Shape

Source NLP variable + bound (from `data/gamslib/raw/fawley.gms`):

```
Variable u(c);          / declared over c = full crude set /
u.up(cr(c)) = crdat(cr,"supply");  / upper bound on refinable subset only /
```

For the upper-bound complementarity to match the matched-pair pattern (one MCP equation per fixed variable instance):

- For each `c ∈ cr` (refinable subset), there is a finite upper bound `crdat(c, "supply")` and the complementarity is meaningful: `crdat(c,"supply") - u(c) ≥ 0 ⊥ piU_u(c) ≥ 0`.
- For each `c ∉ cr` (non-refinable), no upper bound exists; the multiplier `piU_u(c)` is degenerate and must be fixed at zero (matched-pair pairing requires it).

Lagrangian-derived complementarity for `c ∈ cr`:

```
L = ... - piU_u(c) * (crdat(c,"supply") - u(c))    [c ∈ cr only]

∂L/∂piU_u(c) ≤ 0    ⊥    piU_u(c) ≥ 0      for c ∈ cr
piU_u(c) = 0                                       for c ∉ cr
```

### Expected Emit Pattern

The complementarity equation MUST be domain-narrowed to `cr(c)` at the **equation-domain level**, NOT just filtered with a `$`-condition referencing parameters defined over the subset:

```gams
* CORRECT — domain restricted to cr; crdat lookup is safe inside the subset
comp_up_u(cr)$(crdat(cr,"supply") < inf).. crdat(cr,"supply") - u(cr) =G= 0;

* Matched-pair fixup for u(c) instances outside cr
piU_u.fx(c)$(not cr(c)) = 0;
piU_u.fx(cr)$(not (crdat(cr,"supply") < inf)) = 0;
```

Equivalent acceptable form using nested `$`-filters (GAMS short-circuits on nested `$`):

```gams
comp_up_u(c)$(cr(c))$(crdat(c,"supply") < inf).. crdat(c,"supply") - u(c) =G= 0;
piU_u.fx(c)$(not cr(c)) = 0;
piU_u.fx(c)$(cr(c))$(not (crdat(c,"supply") < inf)) = 0;
```

Either form prevents the `crdat(c,"supply")` lookup from triggering `$171` on `c ∉ cr`. The `$(... and ...)` flat-conjunction form currently emitted (see `data/gamslib/mcp/fawley_mcp.gms:273+`) does NOT short-circuit at the parameter-lookup level — GAMS still attempts the lookup before evaluating the conjunction.

### Verification Methodology

```bash
# Step 1: regenerate the emit with the prototype fix
.venv/bin/python -m src.cli data/gamslib/raw/fawley.gms \
  -o /tmp/fawley_mcp.gms --skip-convexity-check --quiet

# Step 2: compile-check — MUST succeed without $171 errors
gams /tmp/fawley_mcp.gms action=c lo=2 o=/tmp/fawley_compile.lst
grep -cE '\*\*\* Error 171' /tmp/fawley_compile.lst
# Expected: 0 (was 3 pre-fix at lines 273×2, 315)

# Step 3: verify the comp_up_u + piU_u.fx emit shape matches the expected pattern
grep -nE '^comp_up_u|^piU_u\.fx' /tmp/fawley_mcp.gms
# Expected: comp_up_u declared over cr (or nested $(cr(c))$(...));
# piU_u.fx has separate fixup for "not cr(c)" instances

# Step 4: PATH solve — should reach MODEL STATUS 1 (Optimal) or
# at minimum a non-$171 outcome (the original $141 cascade at line 381
# may persist if it has a separate root cause; track separately if so)
gams /tmp/fawley_mcp.gms lo=2 | grep -E 'MODEL STATUS|SOLVER STATUS'
```

### PROCEED/REPLAN Signal

**PROCEED** with Sprint 27 Priority 5 implementation if ALL of:

- (a) Compile produces 0 `$171` errors (was 3 pre-fix)
- (b) Emit shape matches one of the two acceptable forms above (domain-narrowed OR nested `$`-filter)
- (c) Tier 0/1 canary byte-stability preserved (no regression on the 11 Tier 0/1 canaries from PR19 widening target list, since complementarity.py is on the PR19 trigger surface)

**REPLAN** if:

- (a) Compile still produces `$171` errors → the proposed shape change is insufficient; investigate whether GAMS evaluates the inner parameter lookup before the outer `$(cr(c))` check (which it shouldn't, but if so, requires equation-domain narrowing only — not nested `$`)
- (b) Tier 0/1 canaries regress → the change to `src/kkt/complementarity.py` is too broad; narrow the trigger condition to "upper-bound complementarity where the bound parameter is declared over a strict subset of the variable's domain"
- (c) Solve produces a different `$171` shape than documented above → file as a separate variant requiring its own Phase 0 derivation

