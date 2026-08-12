# Emitter: ganges-family calibration-assignment stripping (ganges, gangesx unblocked)

**GitHub Issue:** [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289)
**Status:** OPEN — Sprint 25 Priority 2
**Severity:** High — Blocks 2 of 5 Sprint 25 Priority 2 recovered-translate models (`ganges`, `gangesx`) from reaching any `model_optimal` outcome
**Date:** 2026-04-20
**Affected Models:** `ganges`, `gangesx`
**Discovered:** Sprint 25 Prep Task 5 (recovered-translate leverage analysis)
**Labels:** `sprint-25`

---

## Phase 0: Acceptance Gate

*Added Sprint 37 Day 5. CONTRIBUTING §392–447 requires this before any
`src/{ad,kkt,emit}` commit; the issue predates the rule and had none.*

### Hand-Derived KKT Shape

Not a KKT-shape defect — no stationarity row, multiplier or derivative changes.
The defect is that a set of **parameter assignments is absent** from the cold
emit, so the MCP's equations reference symbols that were declared but never
assigned. The formal object is therefore the *availability* of each calibration
parameter at the point the equations read it.

For ganges the 16 unassigned symbols and their consuming rows are:

```
stat_ax  → deltax    stat_deprec  → aid     stat_exscale → aex
stat_invtot → adst   stat_ls → as, deltas   stat_lw → av, deltav
stat_m → aq, deltaq  stat_n → az, deltaz    stat_nd → an, deltan
stat_nm → pnm00      fddef → cg
```

**The decisive precedence question is whether these are computable *cold*.** They
are. Every `.l` value feeding them is **data-initialised** (`ganges.gms:557–745`,
from the `stock`/`dat` tables), and the source's only `solve` is at line **1150**
— *after* the whole calibration block (598–746). So the calibration parameters
depend on pre-solve **data**, not on a solution, and the required precedence
`(.l data init) ≺ (calibration assignment) ≺ (equation definitions)` is
satisfiable without any solve.

Confirmed in the committed cold golden: the `.l` inputs are present
(`ls.l` ×14, `pk.l` ×10, `s.l` ×49) while every calibration assignment is
absent (`deltas`, `as`, `aid`, `adst` — 0 occurrences each).

**⚠ The banked `param(domain) = 0` default is WRONG and must not be used.**
`as`, `deltas`, `av`, `deltav` … are CES/LES **share and scale** parameters;
zeroing them degenerates the production functions, so the MCP would compile
while encoding a *different model* than the NLP and could not legitimately
match. (`SPRINT_36/GANGES_RECOVERY_SEQUENCING.md` §3 step 3 proposed this;
corrected in `SPRINT_37/GANGES_RECOVERY_DESIGN.md` §2.) The fix is to **emit the
real assignments cold**, not to default them.

### Expected Emit Pattern

`ganges_mcp.gms` (cold) must contain the real calibration assignments, ordered
after the `.l` initialisations they read and before the equation definitions:

```bash
OUT=/tmp/i1289/ganges_mcp.gms
mkdir -p /tmp/i1289
.venv/bin/python -m src.cli data/gamslib/raw/ganges.gms -o "$OUT"

# each calibration symbol is assigned at least once
for p in deltax aid aex adst as deltas av deltav aq deltaq az deltaz an deltan pnm00 cg; do
  test "$(grep -cE "^\s*${p}\(" "$OUT")" -ge 1 || echo "FAIL: ${p} still unassigned"
done

# and the assignment follows the .l init it reads
awk '/^\s*ls\.l\(/{seen=1} /^\s*deltas\(/{ if(!seen) {print "FAIL: deltas assigned before ls.l"; exit 1} }' "$OUT"
```

The **presolve** emit must be **byte-identical** — the calibration block already
emits there (`emit_gams.py:2768`), so this change must only add the cold path.

**This is the prep-doc hypothesis** (PR24); the traced surface is below.

### Verification Methodology

1. **Compile count** (the defining measure — `$66` is a compile-time error):
   ```bash
   gams /tmp/i1289/ganges_mcp.gms action=c lo=2
   grep -c '\$66' ganges_mcp.lst      # 16 before, 0 after
   ```
   Repeat **independently for gangesx** — never inferred from ganges.
2. **Presolve byte-stability:** the `--nlp-presolve` emit is byte-identical to
   its pre-change output.
3. **Full-corpus leak gate:** `make leak-check MODEL=ganges,gangesx` →
   unqualified `LEAK GATE PASS`. ⚠ Run at **reduced parallelism** (3 workers):
   at the default 6, ganges/gangesx exceed the hardcoded 600 s emit budget
   (`batch_translate.py:265`) and the verdict is `UNVERIFIED`, not clean
   (Sprint 37 Day 2). ⚠ Note the gate compares **cold** goldens for these two
   models — they carry no presolve golden — which is the right coverage *here*,
   since this issue changes the cold path (Sprint 37 Day 4).
4. **KKT-residual harness** — *not applicable and not run*: the failure is at
   compile, before any solve. Recorded rather than silently skipped.

### PROCEED/REPLAN Signal

**PROCEED** iff `$66` reaches **0** on ganges **and** gangesx independently, the
presolve emit is byte-identical, and the leak gate passes unqualified.

**Traced Fix-Surface (Day-0):** `src/emit/emit_gams.py:2768` — the
`if presolve_include_emitted:` gate wrapping the
`emit_computed_parameter_assignments(..., varref_filter="only_varref_attr")`
call. In the cold path that predicate is False, so the **entire** calibration
block is skipped and the parameters are left declared-but-unassigned. The
partitioning itself is in `original_symbols.py:1716–1742`
(`emit_computed_parameter_assignments`), which classifies a parameter as
"calibration" when any assignment references a `VarRef` attribute and then
propagates that flag transitively. Established by tracing the emitted-vs-source
symbol sets (above) to the single call site that emits them.

**REPLAN** if: the cold assignments cannot be ordered after their `.l` inputs
without restructuring the emit sections; or the leak gate drifts any model other
than ganges/gangesx.

### Bucket / KPI (expected: none from this fix alone)

**This fix does not recover ganges.** It clears the *cold* terminal only. Sprint
37 Day 4 measured the remaining blockers: the presolve path needs #1667 +
**#1668** (currently blocking), and behind those sits the 6th blocker — embedded
`ganges0` **MS-5 @ −386785.5017** vs the standalone source's **MS-2 @
6395.5444**. A second cold blocker (`ac(i+2,r)` in `stat_pc(i)`) also remains
(`GANGES_RECOVERY_DESIGN.md` §2). So this must land as a **0-bucket** compile
correction: Solve stays 108, Match stays 93, and ganges/gangesx stay out of the
recovered set.

### Regression guard

A fixture asserting that a model whose calibration parameters read only
data-initialised `.l` values emits those assignments in the **cold** path —
fail-before/pass-after. Corpus-free where possible
(`SPRINT_37/P7_INFRA_CATALOG.md` §1: a `pytest.skip`-guarded fixture on
`raw/ganges.gms` would be inert in CI, since `ci.yml` provisions only the five
`--fast` models).

---

## Problem Summary

The emitter strips parameter-calibration assignments when translating NLPs that use the "declare-params + initial-solve + calibrate-from-`.l`-values" pattern. The resulting MCP declares the parameters but never assigns values, producing GAMS `Error 66: Use of a symbol that has not been defined or assigned` at the MCP compile step.

## Reproduction

```bash
gams data/gamslib/mcp/ganges_mcp.gms action=c lo=2
# -> 16 × Error 66 — symbols deltax, aid, aex, adst, as, deltas, av, deltav,
#                   aq, deltaq, az, deltaz, an, deltan, pnm00, cg undefined
# -> 2 × final error, 256 solve-stmt errors, compile rejected
```

## Source Pattern (ganges.gms, lines 332–602)

1. Parameters declared with domain-only declarations (lines 332–355)
2. Initial-solve block (runs NLP with literal starting values)
3. Calibration from post-solve `.l` values (lines 598–602):

```gams
deltas(i)$ls.l(i) = (k(i)/ls.l(i))**(1/sigmas(i))*pk.l(i)/sum(r$ri(r,i), pls.l(r));
deltas(i)$ls.l(i) = deltas(i)/(1 + deltas(i));
deltas(i)$(not ls.l(i)) = 1;
as(i) = s.l(i)*(deltas(i)*k(i)**(-rhos(i)) + ...)**(1/rhos(i));
```

When nlp2mcp translates, the emitter includes the Parameter declarations (step 1) but drops the calibration block (step 3). MCP compile then fails because the parameters are referenced by stationarity equations (`stat_ax`, `stat_ls`, etc.) with no values assigned.

## Likely Root Cause

The IR-to-emitter pipeline strips statements that reference variable levels (`.l`, `.m`, `.lo`, `.up`) because those are post-solve quantities. For the calibration-from-solve pattern, this is incorrect: those assignments MUST be emitted in the MCP, wrapped with the `--nlp-presolve` `$include` mechanism so the initial-solve populates the `.l` values first.

## Candidate Fixes

1. **Preserve calibration assignments:** detect "Parameter declared without inline values AND later assigned from `.l` values" pattern; emit both, wrapped to run after the presolve `$include`.
2. **Require `--nlp-presolve`:** flag calibration-pattern models; require the flag to translate them.
3. **Audit IR normalization** for the statement-stripping pass.

## References

- Sprint 25 Prep Task 5: `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Sibling new issues: #1290, #1291, #1292

## Estimated Effort

4–6h

## Files Involved

- `src/ir/normalize.py` — statement-stripping pass
- `src/emit/emit_gams.py` — calibration-block emission
- `data/gamslib/raw/ganges.gms`, `data/gamslib/raw/gangesx.gms` — reference sources
- `tests/unit/emit/` — new emitter test
