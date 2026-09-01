# Positional-vs-Declared-Domain Site Survey (P5)

**Sprint 39 Prep Task 7** · **Measured at:** `52cb2da0`, GAMS **54.2.1** · **Authored:** 2026-09-01

> **⚠ Three of this task's inherited figures are wrong, and one is a live correctness finding.** The repeated-symbol **set** domain is **8× more common** than assumed (16 models, not "as rare as 2"). The repeated **variable** domain is **5** models, not the banked 2. And an emit-level property finds **6 models whose committed goldens already carry a repeated-index guard** — three of them repeats the source never declared.

**Reproducible from the repo.** Every figure below comes from a script in [`artifacts/`](artifacts/README.md), committed alongside this document. Start with `artifacts/mutation_controls.py` — it re-derives the claims §5 rests on and **exits non-zero if either property is vacuous**.

---

## 1. The discriminator this survey turns on

"Resolves an index positionally against a declared domain" is too wide to be a useful filter — `zip()` and `enumerate()` over a domain pair position *i* with position *i* and survive a repeat untouched. **173** subscripted-domain expressions and **33** `zip`-against-a-domain sites exist across `src/kkt/`, `src/ad/`, `src/emit/` and `src/ir/`; almost none of them can break.

What breaks is a **symbol → (position | value) step**, because a repeated symbol collapses it:

| shape | why a repeat breaks it |
|---|---|
| **K2/K3** symbol-keyed map built from a domain | `dict(zip(('i','i'), ('i1','i2')))` = `{'i': 'i2'}` — the first position is silently discarded |
| **K4** `.index(sym)` on a domain | always returns the **first** position |
| **K5** first-match scan with early exit | same, spelled out |

A membership test (`x in domain`) is *not* in this class — `i in ('i','i')` behaves exactly as `i in ('i',)`. There are **27** such sites; they matter only as the **gate** in front of a positional step, which is precisely what happened in elec. They are reported here as context, not as candidates.

**Population: 21 primary sites.** Enumerated by AST scan (`ast.walk` over all four packages), not by grep, so a shape spread across lines cannot hide.

### Positive control — the scan finds both known instances

A survey that cannot rediscover the defects that motivated it is worthless. Both are in the catalog:

| known instance | site the scan flagged |
|---|---|
| **tricp** (S38 D11) — `slp(n,n)` variable domain | `stationarity.py:1500` `_remap_condition_to_domain` (the #1350 consume-once site) |
| **elec** (S38 D12) — `Set ut(i,i)` set domain | `stationarity.py:3931/3954/3966` `_replace_indices_in_expr` |

## 2. The catalog

| site | shape | reach | verdict |
|---|---|---|---|
| `src/kkt/empty_equation_detector.py:127` | symbol-keyed map | 10/15 | **NEEDS A GUARD** |
| `src/ir/condition_eval.py:117` | symbol-keyed map | 9/15 | **NEEDS A GUARD** |
| `src/kkt/stationarity.py:1091` | first position | 2/15 | **NEEDS A GUARD** |
| `src/kkt/stationarity.py:1104` | symbol-keyed store | 2/15 | **NEEDS A GUARD** |
| `src/ad/constraint_jacobian.py:1466` | `symbolic_indices.index(idx)` | 12/15 | **NEEDS A TEST** |
| `src/ad/constraint_jacobian.py:1513` | `symbolic_indices.index(idx)` in a comprehension | 11/15 | **NEEDS A TEST** |
| `src/ad/constraint_jacobian.py:1536` | `symbolic_indices.index(expr.name)` | 4/15 | **NEEDS A TEST** |
| `src/ir/parser.py:6086` | first position | 4/15 | **NEEDS A TEST** |
| `src/ad/constraint_jacobian.py:1474` | `symbolic_indices.index(idx.base)` | 3/15 | **NEEDS A TEST** |
| `src/ir/condition_eval.py:52` | first position | 1/15 | **NEEDS A TEST** |
| `src/kkt/stationarity.py:3432` | `declared_domain[pi]` against a PARAM domain | 1/15 | **NEEDS A TEST** |
| `src/kkt/stationarity.py:4880` | `used_var_positions` | 10/15 | **ALREADY GUARDED** |
| `src/ad/derivative_rules.py:2362` | `enumerate(wrt_indices)` + concrete test | 10/15 | **ALREADY GUARDED** |
| `src/ad/derivative_rules.py:2411` | explicit `seen_sym` duplicate bail-out | 10/15 | **ALREADY GUARDED** |
| `src/kkt/stationarity.py:1500` | `set_declared_domain[pos]` + `_claim` | 3/15 | **ALREADY GUARDED** |
| `src/kkt/stationarity.py:5140` | `used_var` consume-once | 3/15 | **ALREADY GUARDED** |
| `src/kkt/stationarity.py:5148` | `used_var` consume-once | 2/15 | **ALREADY GUARDED** |
| `src/ir/parser.py:5530` | alias expansion | 2/15 | **ALREADY GUARDED** |
| `src/ir/parser.py:6007` | `seen_domain` + minted alias | 2/15 | **ALREADY GUARDED** |
| `src/kkt/stationarity.py:5770` | purpose-built repeated-domain detector | 1/15 | **ALREADY GUARDED** |
| `src/emit/emit_gams.py:795` | `enumerate(domain)` + name match | 0/15 | **NOT REACHABLE (in sample)** |

**`src/kkt/empty_equation_detector.py:127`** — NEEDS A GUARD · reach 10/15

Identical collapse on an EQUATION domain. Two defects meet here: the map collapses, and `_enumerate_domain_instances` yields the full product for a domain a GAMS equation definition would bind diagonally. Reached by 10 of 15.

**`src/ir/condition_eval.py:117`** — NEEDS A GUARD · reach 9/15

`strict=True` catches a LENGTH mismatch but not a KEY collapse: `zip(('i','i'), ('i1','i2'))` yields `{'i': 'i2'}`, silently discarding the first position. This is elec's mechanism in a second layer, and nothing upstream de-duplicates a SET or PARAM domain. Reached by 9 of 15 sampled models.

**`src/kkt/stationarity.py:1091`** — NEEDS A GUARD · reach 2/15

`_pos` returns the first position of a symbol in a VarRef's index tuple; `bindings` is then keyed by equation index and `var_domain[binding_position]` resolved positionally. With a repeated tuple the binding position is always the first occurrence. The `len(bindings) != 1` bail-out rejects the multi-index case but not the single-index one.

**`src/kkt/stationarity.py:1104`** — NEEDS A GUARD · reach 2/15

Same site, the storing half. Included separately because a guard could live at either end.

**`src/ad/constraint_jacobian.py:1466`** — NEEDS A TEST · reach 12/15

Highest-reach site in the sample. `.index()` returns the FIRST position, so a repeated `symbolic_indices` substitutes every occurrence to `concrete_indices[0]` — `slp(n1,n2)` would emit as `slp(n1,n1)`. Safe **today** only because `dedupe_repeated_variable_domains` (Issue #1062) rewrites repeated VARIABLE domains before differentiation. That pass covers variables only, so the protection is upstream and incidental, not local.

**`src/ad/constraint_jacobian.py:1513`** — NEEDS A TEST · reach 11/15

Builds `free_concrete` by `.index()` per free symbol; a repeat silently maps both to the first concrete value. Same upstream-only protection.

**`src/ad/constraint_jacobian.py:1536`** — NEEDS A TEST · reach 4/15

Bare `SymbolRef` substitution (#730). Same shape.

**`src/ir/parser.py:6086`** — NEEDS A TEST · reach 4/15

Anchors a multidim set condition at the first match, then checks contiguity. A repeated symbol can anchor the window at the wrong start. Partly mitigated by the alias substitution 80 lines above (site 6007).

**`src/ad/constraint_jacobian.py:1474`** — NEEDS A TEST · reach 3/15

Same mechanism on the `IndexOffset` base (#1045). Same upstream-only protection.

**`src/ir/condition_eval.py:52`** — NEEDS A TEST · reach 1/15

Searches for the `*` sentinel, not a set symbol. `p(*,*)` is expressible; the `star_pos >= 2` test happens to reject it, but `p(i,*,j,*)` is not covered by that argument. Reached by 1 of 15.

**`src/kkt/stationarity.py:3432`** — NEEDS A TEST · reach 1/15

Positional throughout (pi -> pi), so no symbol->position step. But `offset_map` is symbol-keyed, so a param declared `rail(i,i)` (ferts) receives the SAME offset at both positions. Whether that is right depends on the intent, which the code cannot see. Reached by 1 of 15.

**`src/kkt/stationarity.py:4880`** — ALREADY GUARDED · reach 10/15

Consume-once over variable-domain positions. Reached by 10 of 15 — the most-reached guarded site.

**`src/ad/derivative_rules.py:2362`** — ALREADY GUARDED · reach 10/15

Feeds the duplicate check below. Reached by 10 of 15.

**`src/ad/derivative_rules.py:2411`** — ALREADY GUARDED · reach 10/15

The comment names this class exactly: 'duplicates would overwrite earlier entries'. A third independent guard, in the AD layer. Reached by 10 of 15.

**`src/kkt/stationarity.py:1500`** — ALREADY GUARDED · reach 3/15

The #1350 consume-once fix: `used_slots` prevents two positions claiming the same variable-domain slot. This is one of the two known instances and is the survey's positive control for the 'guarded' verdict.

**`src/kkt/stationarity.py:5140`** — ALREADY GUARDED · reach 3/15

Exact canonical match with `used_var` preventing double-claim.

**`src/kkt/stationarity.py:5148`** — ALREADY GUARDED · reach 2/15

Common-root fallback, same `used_var` set.

**`src/ir/parser.py:5530`** — ALREADY GUARDED · reach 2/15

Its own comment cites 'tfp is an alias for tf and domain is (tf,tf)' — the parser already alias-expands a repeated PARAM domain on this path.

**`src/ir/parser.py:6007`** — ALREADY GUARDED · reach 2/15

Mints an alias for the second occurrence, 'e.g. a(n,n) -> (n,np)'. The same remedy as Issue #1062, applied at the parser for SET domains — but only on this branch.

**`src/kkt/stationarity.py:5770`** — ALREADY GUARDED · reach 1/15

Exists FOR this class: requires >= 2 var-domain positions canonicalising to the same set. Its own docstring records 15 of 142 models reaching conjunct 1. Reached by 1 of 15 here.

**`src/emit/emit_gams.py:795`** — NOT REACHABLE (in sample) · reach 0/15

0 of 15 sampled models executed this line, including both known instances and five of the six emit-level offenders (`nonsharp` was identified later, by the generalised matcher, and was not in the traced sample). NOT a proof of unreachability — it is a measured absence over a 15-model sample chosen to be adversarial for this class, and it is recorded as such.

---

## 3. The organising fact: one sub-shape is globally guarded, two are not

`dedupe_repeated_variable_domains` (Issue #1062, tricp's fix) runs unconditionally at `src/cli.py:476`, **before differentiation**, and rewrites the second and later occurrences of a repeated symbol to a freshly minted alias. It iterates `for var_name in list(model_ir.variables)` — **variables only**. `model_ir.sets` and `model_ir.params` are read solely to populate the `taken` collision namespace.

| declared domain repeats a symbol in a… | globally guarded? |
|---|---|
| **variable** domain | ✅ yes — neutralised at the source, before any consumer sees it |
| **set** domain | ❌ no |
| **parameter** domain | ❌ no |

This is why so many `NEEDS A TEST` verdicts above are *"safe today, but by something upstream and incidental"*. The `.index()` family in `constraint_jacobian.py` is the highest-reach shape in the whole catalog (12/15 and 11/15 models), and its repeat-safety rests entirely on a pass that covers one of the three sub-shapes. **The audit's cheapest possible outcome is to make that dependency explicit rather than accidental.**

## 4. Corpus incidence (Unknown 5.2)

**Two independent methods, deliberately.** An IR census over all 219 models (`parse_model_file`, then a **case-insensitive** repeat test — `len(domain) != len({x.lower() for x in domain})` — per symbol table, because GAMS identifiers are case-insensitive, so `p(I,i)` is a repeat) and a source-level regex prescan of the raw `.gms` files. They agree on **24** models; the union is **44**.

| kind | models | ∩ the 142 convex candidates |
|---|---|---|
| **set** domain | **16** | 11 |
| **parameter** domain | **21** | 16 |
| **variable** domain | **5** | 4 |
| **equation** domain | 0 | 0 |
| **any** | **34** | **25** |

**Both banked figures are wrong.**

- The plan records the *variable*-domain case as **"exactly two models: `tricp`, `ferts`"**. It is **five** — `ferts`, `lop`, `maxmin`, `sarf`, `tricp`. `lop` declares `dtr(s,s,s,s)`, a **four-fold** repeat.
- Unknown 5.2's assumption is that the *set*-domain shape is **"as rare as the variable-domain shape"**. It is **16 models, 8×** the variable count — and the **parameter** shape, which no one had counted at all, is larger still at **21**.

**Coverage limits, stated rather than buried.** The IR census could not parse **41 of 219** models (10 of them prescan candidates: `andean`, `dinam`, `emfl`, `epscm`, `gqapsdp`, `kqkpsdp`, `netgen`, `phosdis`, `qp1x`, `sddp` — `dinam` timed out at 120 s, several `$include` a file the corpus does not carry). Those 10 are counted from the source prescan only, so their **kind** breakdown is unknown. The per-kind figures above are therefore **lower bounds**.

### Is a matching model silently wrong? (5.2 Q3)

**11 of the 34** currently match: `bearing`, `cesam2`, `chenery`, `elec`, `gussrisk`, `kand`, `maxmin`, `mexss`, `robustlp`, `srkandw`, `weapons`. **Carrying the declaration shape is not the same as being wrong** — §5's emit-level check is what distinguishes them, and it puts exactly **one** matching model in the suspect set (`gussrisk`), with a latent rather than an active defect. (`weapons` is separately known to be a **spurious** presolve match — S38 Day 10, reported and uncorrected.)

## 5. The property test (Unknown 5.3) — and what it does *not* cover

### P1 — no emitted equation HEAD repeats a controlling index symbol

Stated over the **emitted output**, because that is where the GAMS semantics bite: a repeated controlling index in an equation *definition* binds to the same element, so `stat_slp(n,n)..` generates only the diagonal.

- **193 goldens, 3,100 equation heads, 0 violations, under 3 s.** Runs at full corpus scale; no sampling needed. (Measured 1.3–2.2 s for P1+P2 together across runs — quoted as a bound rather than a point figure, because it is wall-clock and does not reproduce to two significant figures.)
- **Mutation-killed, not merely green.** With `dedupe_repeated_variable_domains` monkeypatched to a no-op, tricp emits **4** violations — `stat_slp(n,n)`, `stat_sln(n,n)`, `comp_lo_slp(n,n)`, `comp_lo_sln(n,n)`. The property detects the real defect.
- **⚠ And that is exactly the answer to 5.3 Q5: the #1062 guard makes P1 trivially true *for variable domains*.** P1 is a regression test on one sub-shape, not a property covering the class.
- **Proof: P1 scores 0 on elec's pre-fix golden.** elec's defect was never in a head — it was in a `$(...)` guard inside the body.

### P2 — no emitted `$(...)` guard references a **symbol** at a repeated index

**Not set-specific:** the matcher is `name(x,x)` for any symbol, because the live hits are parameters (`ts2`, `tranc`, `vs`, `covar`) as much as sets. The complement. Scoped to guards **on purpose**: `Set ut(i,i)` in the emitted declaration block is the model's own legitimate declaration, and a naive whole-file form flags it in elec both before *and* after the fix — a false positive that would have made the check useless.

- Control: **elec pre-fix 1 violation (`$(ut(i,i))`), elec today 0.**
- **⚠ P2 finds 9 violations across 6 CURRENT goldens.**

| model | emitted | source declares it repeated? | assessment |
|---|---|---|---|
| `dinam` | `1$(ts2(te,te))` | ❌ source has `ts2(te,tep)` | **manufactured.** `ts2(te,tep) = 1$(ord(te) > ord(tep))` is strictly triangular ⇒ **identically false**; the term is silently zeroed. elec's exact shape. |
| `egypt` | `1$(tranc(rp,rp))` | ❌ source has `Table tranc(r,rp)` | **manufactured.** A self-transfer cost; the diagonal is absent ⇒ the term drops. |
| `turkpow` | `1$(vs(v,v))`, `1$(vs(t__kkt1,t__kkt1))` | ❌ source has `vs(t,v)` | **manufactured, and the MIRROR case.** `vs(t,v) = ord(t) >= ord(v)` ⇒ `vs(v,v)` is identically **TRUE**, so the guard is a no-op and the term is included for *every* instance instead of a triangle. Silently **over**-inclusive. `t__kkt1` is a KKT-minted name, so this guard was generated, not copied. |
| `shale` | `1$(ts(tf,tf))` | ✅ `ts(tf,tf)` | declaration-derived. `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` ⇒ identically false. |
| `nonsharp` | `inter(col,col,stm)`, `inter(col__kkt1,col__kkt1,stm)` | ✅ `Set inter(col,col,stm)` | **3-arity — invisible to the original binary matcher** (PR #1718 review). The source only ever assigns off-diagonal pairs (`inter(colp,col,stm)`), so `inter(col,col,stm)` is identically false. `col__kkt1` is KKT-minted, so that one is **manufactured**. Convexity `excluded`, no MCP solve — outside the 142 candidates. |
| `gussrisk` | `covar(stocks,stocks)$(NOT (…)) = 0;` | ✅ `covar(stocks,stocks)` | declaration-derived, on an **assignment**. The repeat is in *both* the LHS and the guard; the **LHS** is what narrows the NA-guard to the diagonal, and P2 sees only the guard (gap below). **Latent:** `covar` is computed and never NA, so today's answer is unaffected. The one **matching** model in the suspect set. |

**A third sub-shape falls out of this that neither known instance showed:** a manufactured repeat can be identically **true** (`turkpow`) as easily as identically false (`elec`, `dinam`, `shale`). An "is this guard always false?" check would miss half of them. The property must be *"the index repeats"*, not *"the guard is unsatisfiable"*.

### Are there legitimate counter-examples? (5.3 Q2)

**For P1, no** — 0 violations in 3,100 heads. A repeated controlling index in an emitted head is never what we want, because the MCP then has unmatched columns.

**For P2, yes, and they are why the scoping matters** — a declaration (`Set ut(i,i)`) and a genuinely diagonal reference are both legitimate. Restricting P2 to the CONTENT of `$(...)` guards removes the declaration class. `gussrisk` and `shale` show the residue: a *reference* built from the declared domain's own symbols, which is legitimate syntax carrying an illegitimate scope.

### Cost and home

**⚠ P2's known gap, found in review of this PR.** It scans **guard content only** and does not inspect an assignment's **left-hand side**. `gussrisk` is caught only because its repeat appears in *both* the LHS and the guard — **a repeated LHS with a clean guard would be missed.** The line filter (`".." in line or "=" in line`) merely selects candidate lines; it does not widen what is scanned. Closing this is a one-line extension and belongs with P2's graduation into a gate, not with prep.

Both properties are pure text scans of `data/gamslib/mcp/`: **under 3 s over 193 goldens** (1.3–2.2 s measured), no model re-emission, no GAMS. They belong beside the existing golden-level gates rather than in the unit suite, and neither needs to sample.

## 6. Ranked recommendation for P5

P5 is **0-bucket by design**; nothing below asks for a bucket move.

1. **Land P2 as a gate first.** It is the only artefact here that finds live defects, it runs in 2.2 s, and its 5 hits are a ready-made work list. Landing it *before* any guard means the guards have a fail-before.
2. **Guard the two symbol-keyed `dict(zip(...))` collapses** — `condition_eval.py:117` and `empty_equation_detector.py:127`. Highest reach among unguarded sites (9/15 and 10/15), smallest fix, and `strict=True` already gives a false sense of safety there.
3. **Make the `constraint_jacobian.py` `.index()` family's dependency explicit** — 4 sites, the highest-reach shape in the catalog, safe only because of a pass covering one of three sub-shapes.
4. **Then `stationarity.py:1091/1104`.** Lower reach (2/15), genuinely unguarded.
5. **Do not re-guard the 9 `ALREADY GUARDED` sites** — three independent remedies already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser alias substitution). Add tests that pin them; the `NEEDS A TEST` verdicts are exactly this.

**⚠ The four `NEEDS A GUARD` sites are candidates, not confirmed defects.** Each needs the Day-0 trace the S38 retrospective requires — three of four S38 gates named the wrong layer.

## 7. What this survey does not establish

- **It did not re-derive whether the 9 P2 hits change any answer.** `dinam`, `egypt`, `shale`, `turkpow` are all `mcp_solve: failure` today and `nonsharp` is convexity-`excluded` with no MCP solve, so a wrong term is not currently reaching a reported KPI; `gussrisk` matches but its instance is latent on this data. Confirming each is P5 execution work, not prep.
- **`emit_gams.py:795` is "not reachable *in sample*", not "not reachable".** 0 of 15 models executed it, and the sample was chosen adversarially for this class (both known instances, five of the six emit-level offenders, plus controls — `nonsharp` surfaced only after the matcher was generalised in review). That is a measured absence over 15 models, not a proof — and it is the one verdict in the catalog resting on absence of evidence.
- **The per-kind census is a lower bound** — 41 of 219 models did not parse.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 7
**Last Updated:** 2026-09-01
