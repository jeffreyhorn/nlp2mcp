# ISSUE #1667 — ganges/gangesx: deferred `.l`-dependent bounds emitted BEFORE the presolve `$include`

**Status:** 🔶 **CONTROL VERIFIED, LANDING BLOCKED** — the fix itself is correct and measured
(Sprint 37 Day 4: `rPower` cleared, `rc=0` on both ganges and gangesx, and it correctly
co-applies to `korcge`, verified benign). It **cannot ship alone**: reaching this defect
requires the `$149` `_diff_prod` rebind, which over-fires on `prolog` — see **#1668**.
**Sprint:** 37 (P2, the ganges/gangesx recovery cascade) · **Prep:** Task 5 §3
**File:** `src/emit/emit_gams.py` — the Issue #921 deferred-bounds block (`:2632–2646`)
**Design:** `docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md` §3

## Problem

Under `--nlp-presolve`, generation aborts with
`rPower: FUNC DOMAIN: x**y, x=0,y<0` in `prods(i)` for four sectors, because the
emitted MCP applies `ls.fx(i)$(not ls.l(i)) = 0` **before** the `$include` that
sets `ls.l`. Source order is 593 (`ls.l`) then 1071 (`ls.fx`); emitted order is
484 (`ls.fx`) then 515 (`$include`). The guard therefore fires for every sector
and pins `ls` to 0, and `prods(i)` evaluates `0**(-rhos(i))`.

## Fix (design)

Under `--nlp-presolve`, **do not emit the deferred `.l`-dependent bounds block at
all** — the `$include` re-executes the source's own bound statements at the
correct point, after the `.l` values exist. Control B of Task 5 §3.

The gate already exists in scope: `presolve_will_emit`
(`emit_gams.py:1896`) is the same predicate that guards three sibling
`$include`-supplied decisions (`:1917`, `:1977`, `:2326`).

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

This is **not** a KKT-shape defect — no stationarity row, multiplier, or
derivative changes. It is a **statement-ordering** defect in the emitted GAMS
program's initialization prologue, so the correct formal object is the execution
order of the bound statements, not a Lagrangian.

For the source model, the relevant statements and their required precedence are:

```
(1)  ls.l(i)            = stock("self-empl",i)*100        [ganges.gms:593]
(2)  ls.fx(i)$(not ls.l(i)) = 0                           [ganges.gms:1071]
```

`(2)` reads `ls.l`, so correctness requires **(1) ≺ (2)**. GAMS evaluates the
guard `$(not ls.l(i))` against the level in effect at execution time; with
`ls.l = 0` the guard is universally true and `ls` is fixed to 0 for all `i`.

The equation that then fails is

```
prods(i).. s(i) =e= as(i)*( deltas(i)*k(i)**(-rhos(i))
                    + ((1-deltas(i))*ls(i)**(-rhos(i)))$(not si(i)) )**(-1/rhos(i))
```

with `rhos(i) > 0`, so `ls(i)**(-rhos(i))` = `0**negative`, which is outside the
domain of `**`. The four failing sectors are exactly those reaching the guarded
term: `pub-infr` is excluded by `$(not si(i))` and `agricult` is the `sa` subset
handled separately.

**Invariant to preserve:** under `--nlp-presolve` the emitted prologue must not
apply any `.l`-dependent bound statement before the `$include` establishes those
`.l` values.

### Expected Emit Pattern

The emitted presolve MCP must contain **no**
`* Deferred Variable Bounds (depend on .l values)` section, and no
`ls.fx(...)$(not ls.l(...))` statement ahead of the `$include`.

⚠ **Run these against a freshly-emitted file, not a golden: ganges and gangesx
have no committed presolve golden** (only 17 of the 153 golden-carrying models
do). This also bounds what the leak gate can see — `--expect-drift ganges,gangesx`
compares their **cold** goldens only, so the presolve output this issue changes
is not golden-tracked at all and must be checked directly.

```bash
OUT=/tmp/i1667/ganges_mcp_presolve.gms
mkdir -p /tmp/i1667
.venv/bin/python -m src.cli data/gamslib/raw/ganges.gms --nlp-presolve -o "$OUT"

# 1. no deferred-bounds section at all
test "$(grep -c 'Deferred Variable Bounds' "$OUT")" -eq 0 || echo "FAIL: block still emitted"

# 2. no .l-dependent guard ahead of the $include (exits 1 and names the line if found)
awk '/\$include/{exit 0}
     /ls\.fx.*not ls\.l/{printf "FAIL: pre-$include guard at line %d\n", NR; exit 1}' "$OUT"
```

Both checks verified against the real before/after emits: pre-fix the awk reports
`FAIL: pre-$include guard at line 500` and exits 1; post-fix it exits 0.

The **cold** (non-presolve) emit must be **byte-identical** — the block is only
redundant when an `$include` re-supplies it, so the change is gated on
`presolve_will_emit` and must not touch the cold path.

**This is the prep-doc hypothesis** (PR24); the `file:line` surface is the traced
one below.

### Verification Methodology

1. **Reproduce the abort** on the current emit:
   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/ganges.gms --nlp-presolve -o /tmp/g/ganges_mcp_presolve.gms
   gams /tmp/g/ganges_mcp_presolve.gms curdir=/tmp/g
   grep -E "rPower|EXECERROR" /tmp/g/ganges_mcp_presolve.lst    # expect FUNC DOMAIN, EXECERROR = 1
   ```
2. **After the fix:** the same run reaches `rc = 0` with **no** `rPower` and no
   `EXECERROR`, for **both** ganges and gangesx.
3. **Cold-path byte-stability:** the non-presolve emit is byte-identical to the
   committed golden (this fix must be invisible without `--nlp-presolve`).
4. **Full-corpus leak gate:** `make leak-check MODEL=ganges,gangesx` →
   unqualified `LEAK GATE PASS`. ⚠ Run at **reduced parallelism**: ganges emits
   in 259–293 s standalone and the sweep's per-model budget is a hardcoded 600 s
   (`scripts/gamslib/batch_translate.py:265`), so at the default 6 workers these
   two models time out and the verdict is `UNVERIFIED` rather than clean
   (Sprint 37 Day 2).
5. **KKT-residual harness** — *not applicable and not run*: the abort happens at
   generation, before any solve, so there is no residual to evaluate. Recorded
   explicitly rather than silently skipped.

### PROCEED/REPLAN Signal

**PROCEED** iff: the presolve emit reaches `rc = 0` with no `rPower` on **both**
ganges and gangesx; the cold emit is byte-identical; and the leak gate passes
unqualified.

**Traced Fix-Surface (Day-0):** `src/emit/emit_gams.py:2632–2646` — the
`if deferred_bound_lines:` block under the *"Issue #921: Emit deferred bounds
(.lo/.up/.fx that reference .l values) after .l initialization"* comment, inside
`emit_gams_mcp` (`:1710`). Established by grepping the emitted marker string
`"Deferred Variable Bounds (depend on .l values)"` to its single emission site,
then confirming that `presolve_will_emit` (`:1896`) is in scope there and already
gates the analogous `$include`-supplied decisions at `:1917`, `:1977` and
`:2326`. `_emit_nlp_presolve` and the KKT/AD layers are **not** touched.

**REPLAN** if: removing the block does not clear `rPower` (⇒ the level-0 pin has
another source); the cold emit drifts (⇒ the gate is wrong); or the leak gate
reports drift on any model other than ganges/gangesx.

### Bucket / KPI (expected: none from this fix alone)

**This fix does not recover ganges.** Task 5 measured the next blocker behind it:
with `rPower` removed, the embedded `ganges0` NLP solves **MS-5 Locally
Infeasible @ −386785.5017** while the identical standalone source solves **MS-2
Locally Optimal @ 6395.5444** — the genuine #1378/#1424 embedded-NLP-divergence
class. So ganges/gangesx stay `path_syntax_error`, Solve stays 108, and this
must be landed as a **0-bucket ordering correction**. Claiming a bucket gain here
would be wrong. P2's +2 remains gated on the divergence, which is a separate
issue.

### Regression guard

A fixture asserting that a presolve emit carrying a `.l`-dependent bound
statement emits **no** deferred-bounds block, while the cold emit still does —
fail-before/pass-after, corpus-free where possible (`SPRINT_37/P7_INFRA_CATALOG.md`
§1 — a `pytest.skip`-guarded fixture on `raw/ganges.gms` would be inert in CI,
since `ci.yml` provisions only the five `--fast` models).

## Control result (Sprint 37 Day 4)

| gate | result |
|---|---|
| `rPower` cleared, `rc = 0` | ✅ **both** ganges and gangesx |
| `$141` / `$145` / `$149` | ✅ 78 / 3 / 9 → **0 / 0 / 0** |
| deferred-bounds block absent under presolve | ✅ both |
| full-corpus leak gate | ❌ **LEAK** — `korcge` (benign, verified) and **`prolog`** (harmful, from `$149` — **#1668**) |
| bucket | 0 — the 6th blocker is unmoved (embedded `ganges0` **MS-5 @ −386785.5017** vs standalone MS-2 @ 6395.5444) |

**`korcge` co-application is correct, not collateral.** Its deferred bounds *are* source
statements, so the `$include` re-supplies them; it still solves `MODEL STATUS 1 Optimal`
at **339.2130**, exactly the DB's recorded match. When this lands, `korcge` belongs in
`--expect-drift` alongside ganges/gangesx.

## References

- `docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md` §3 — the two `/tmp` controls
- `src/emit/original_symbols.py:1832–1848` — the #1378 `$include`-supplied skip this extends
- `emit_gams.py:1830` — the var-init `.l` skip precedent, gated the same way
- Issue #921 — the original deferred-bounds ordering fix this refines
