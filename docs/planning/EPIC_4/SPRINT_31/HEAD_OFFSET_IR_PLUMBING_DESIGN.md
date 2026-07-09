# mine Head-Offset IR-Plumbing Design + Round-Trip Reproduction

**Task:** Sprint 31 Prep Task 3 (Priority 1 foundation — the critical-path anchor)
**Date:** 2026-07-08
**Owner:** Development team (IR/AD/KKT specialist)
**Scope:** design/analysis only — no `src/` change (all probes were read-only parses; the committed goldens are untouched).

---

## 0. Executive summary — the round-trip is a field addition, not a deep normalize rewrite (favorable)

Sprint 30 Day 6 REPLAN'd #1443 for a *foundational* reason: the shared 3-site head-offset index-map helper the emit architecture needs **cannot be built** until the head-offset position+amount is plumbed through the IR — today `pr.has_head_domain_offset` is a bare `bool` and the `l+1` head is discarded, so the helper has nothing to read. This task turns that blocker into a concrete IR-plumbing design and, critically, **empirically pins where the detail is lost and how cleanly it round-trips.**

**Headline findings (all empirically confirmed on `data/gamslib/raw/mine.gms`):**

1. **The head offset is discarded at PARSE, not at normalization.** For `pr(k,l+1,i,j)$c(l,i,j)..`, the parser already stores `pr.domain = ('k','l','i','j')` (base labels) + `has_head_domain_offset=True` — the `l+1` on the domain head is gone before normalize ever runs. The culprit is `_domain_list_has_offset` (`src/ir/parser.py:932`), which walks the domain elements and returns **only a bool**, and `_extract_domain_indices` (`:956`), which strips each element to its base name. **Normalization does not re-collapse anything** — so the round-trip is not a normalize problem.
2. **The parameter offsets `li(k)`/`lj(k)` are already preserved** — they live in the equation body (`lhs_rhs`) as `IndexOffset(base='i', offset=ParamRef(li(k)))` / `IndexOffset(base='j', offset=ParamRef(lj(k)))`. Only the **domain head offset** (position `l`, δ=+1) is lost; it survives *implicitly* in the RHS body `x(l+1,i,j)` but is not stored as a domain-level attribute.
3. **`EquationDef` already has the exact precedent to mirror.** Issue #1327 added `declaration_domain` — the un-collapsed original domain stored *alongside* the collapsed body `domain`. The head-offset detail is the same shape of problem: store the per-position offset alongside the collapsed base domain.
4. **The round-trip is therefore a FIELD ADDITION on `EquationDef` + copy-through at the ~3 reconstructor sites — not a normalize rewrite.** `NormalizedEquation` (`src/ir/normalize.py:13`) does not carry `has_head_domain_offset` at all; the KKT/emit consumers read the original `EquationDef` (via `model_ir.equations[name]`). So the new field is available to every consumer as long as (a) the parser populates it and (b) the equation-reconstructing sites (`complementarity.py`, `sqr_reformulation.py`) copy it, exactly as they already copy `has_head_domain_offset`. **Unknown 1.1 = ✅ VERIFIED (favorable): a field addition, not a deep normalize rewrite.**

This de-risks P1's foundational Phase 1: the IR change is additive with a bounded, enumerable touchpoint set, and its **emit blast radius is zero until a consumer reads the field** (Unknown 1.4). The hard, REPLAN-prone work remains Phase 2 (the shared helper + the `comp_pr` head×parameter-offset coupling, `ISSUE_1443` Day-7).

---

## 1. Where the head-offset detail is lost today (empirical trace)

Parsing `data/gamslib/raw/mine.gms` (read-only) yields, for the head-offset equation `pr`:

```
pr.domain                 = ('k', 'l', 'i', 'j')          # base labels — the l+1 head already collapsed
pr.has_head_domain_offset = True                          # the ONLY surviving head-offset signal (a bare bool)
pr.declaration_domain     = None                          # (no #1327 subset-decl divergence here)
pr.condition              = SetMembershipTest(c, (l,i,j)) # the $c(l,i,j) guard
pr.lhs_rhs[0] (LHS)       = x(l, IndexOffset('i', ParamRef(li(k))), IndexOffset('j', ParamRef(lj(k))))
pr.lhs_rhs[1] (RHS)       = x(IndexOffset('l', Const(1.0)), i, j)     # the l+1 head survives ONLY here, implicitly
```

So the source `pr(k,l+1,i,j)` loses the `+1` on domain position `l`; the emit layer can only *infer* it from the body RHS or the `ord(l)<=card(l)-1` condition. The two lossy parser functions:

- **`_domain_list_has_offset` (`src/ir/parser.py:932`)** — recursively walks each `domain_element` subtree, returns `True` if any has a `linear_lead`/`linear_lag` node, else `False`. It **sees** the position (enumeration order of `node.children`) and the offset node (the `+1`) but collapses both to a single bool. The result is stored at `parser.py:3856` (`head_has_offset = _domain_list_has_offset(domain_list_node)`) and passed to the `EquationDef` constructor at `parser.py:3952` (`has_head_domain_offset=head_has_offset`).
- **`_extract_domain_indices` (`src/ir/parser.py:956`)** — extracts *base identifiers only* (`i+1 -> ['i']`), so the stored `domain` is the base tuple.

**The IR already has the machinery to represent the offset:** `IndexOffset(base, offset, circular)` (`src/ir/ast.py:346`) — `l+1` is exactly `IndexOffset(base='l', offset=Const(1.0), circular=False)` — and the parser's per-index builder (`parser.py:1231–1405`, `_index_expr_to_offset`) already produces these for body indices. The head-offset loss is purely that `_domain_list_has_offset` throws the structure away.

---

## 2. IR storage design — `EquationDef.head_domain_offsets` (mirror `declaration_domain`)

Add one field to `EquationDef` (`src/ir/symbols.py:135`), positioned next to `declaration_domain` and documented with the same rationale:

```python
@dataclass
class EquationDef:
    name: str
    domain: tuple[str, ...]                 # collapsed base labels — ('k','l','i','j')
    ...
    has_head_domain_offset: bool = False    # KEEP (back-compat convenience; = any(head_domain_offsets))
    declaration_domain: tuple[str, ...] | None = None
    # NEW (Sprint 31 P1 Phase 1): the per-position domain head offset, aligned to `domain`.
    # Element k is the IndexOffset for domain position k, or None if that position has no
    # linear lead/lag. For pr(k,l+1,i,j): (None, IndexOffset('l', Const(1.0), False), None, None).
    # Mirrors declaration_domain (#1327): the un-collapsed detail stored ALONGSIDE the collapsed
    # `domain`, so the KKT/emit layer re-applies the base<->head correspondence instead of
    # re-deriving it from the body. Circular (++/--) offsets stay excluded (as today).
    head_domain_offsets: tuple[IndexOffset | None, ...] | None = None
```

**Design choices:**

- **Per-position tuple aligned to `domain`** (not a dict) — matches how `domain`, `up_expr_map` keys, and the emit sites already index by domain position; `None` at non-offset positions keeps alignment trivial. For mine: `(None, IndexOffset('l', Const(1.0), False), None, None)`.
- **`has_head_domain_offset` stays** as a derived convenience (`= any(o is not None for o in head_domain_offsets)`), so the ~8 existing read sites keep working unchanged during the migration; new code reads `head_domain_offsets`.
- **`None` (not `()`) default** distinguishes "not yet plumbed / no offset" from "computed, empty" — but since it is populated at parse for every equation, consumers can treat `None` as "no head offset" safely.
- **Type reuse:** `IndexOffset` already carries `(base, offset, circular)` — the design needs no new type. The `offset` is `Const(1.0)` for `+1`; a general `IndexOffset` also covers `l-1` / symbolic heads for free.

**Producer (1 site):** `_domain_list_has_offset` is replaced/supplemented by a new `_domain_list_head_offsets(node) -> tuple[IndexOffset | None, ...]` that reuses the existing `_index_expr_to_offset` logic per domain position; `EquationDef(...)` at `parser.py:3952` gains `head_domain_offsets=...`. `has_head_domain_offset` becomes `any(...)` over it.

---

## 3. Normalize round-trip design + blast-radius guard (the copy-through touchpoints)

**normalize is a passthrough — no change required there.** `normalize_equation` (`src/ir/normalize.py:90`) reads `eq.domain` and builds a *separate* `NormalizedEquation` (`normalize.py:13`) whose fields are `name / domain_sets / index_values / relation / expr / expr_domain / rank / condition / source_location`. It does **not** carry `has_head_domain_offset` and does **not** reconstruct `EquationDef`, so it cannot lose the new field. The KKT/emit consumers that need the head offset read the original `EquationDef` from `model_ir.equations[name]`, which is preserved across normalization.

**The only round-trip risk is the equation-*reconstructing* sites** — code that builds a *new* `EquationDef` from an existing one and must copy the new field, exactly as it already copies `has_head_domain_offset`:

| Reconstructor touchpoint (must copy `head_domain_offsets`) | Current `has_head_domain_offset` copy |
|---|---|
| `src/kkt/sqr_reformulation.py:88` + `:108` (square-reformulation rebuilds) | `:95`, `:115` |
| `src/kkt/complementarity.py:242` (the constraint-equation rebuild) | `:256` |

(The other `EquationDef(...)` constructions in `complementarity.py` — the `comp_*`/`equality_eq` multiplier/complementarity equations at `:305/:384/:404/…` — are *derived* KKT equations, not the source constraint; they do **not** copy `has_head_domain_offset` today and must **not** grow a head offset. The Phase-2 helper reads the head offset from the **source** `EquationDef` (the one at `complementarity.py:242`), which is the correct and only carrier.)

**Consumer read sites (unchanged interface, migrate to the richer field in Phase 2):**

- `src/kkt/stationarity.py` — the `stat_x` cross-term builder `_try_build_param_offset_crossterm` (`:5618`, called `:5825`) — Site 3.
- `src/emit/emit_gams.py` — `_emit_nlp_presolve` (`:1354`) — the `lam_pr.l = abs(pr.m)` dual transfer — Site 2.
- `src/emit/emit_gams.py:2951` + `:3125`, `src/emit/equations.py:1072/:1103/:1173` — the `comp_pr` head-var / lead-lag emit — Site 1.

**Blast-radius guard (Unknown 1.4):** the field addition itself changes **no emit output** — adding + populating `head_domain_offsets` is inert until a consumer reads it (verified conceptually: no emit path branches on it in Phase 1). The meaningful blast radius is the **Phase-2 helper**, gated (as today) to the *non-`Const` parameter-offset* shape, which fires on **mine only** (the Sprint-28 gate note: launch/camshape/otpop/trnsport byte-identical). A read-only corpus sample confirms head-offset *equations* are common but the param-offset coupling is rare:

| model | head-offset equation(s) | param offset on body? |
|---|---|---|
| **mine** | `pr(k,l,i,j)` | **yes** (`li(k)`/`lj(k)`) — Phase-2 target |
| robert | `sb(r,tt)` | no (constant `+1`) — objective-gradient bug, not this track |
| camshape | `eqrdiff(i)` | no |
| ramsey | `kk(t)` | no |
| abel | `stateq(n,k)` | no |
| launch / otpop / trnsport / chenery / weapons | (none) | — |

**Phase-1 verification step (in-sprint):** a full-corpus parse-scan enumerating every `has_head_domain_offset=True` equation + a byte-diff of all goldens after the field addition, to confirm **zero golden changes** (the field is inert) before Phase 2 touches any emit site.

---

## 4. Round-trip unit reproduction (the Phase-1 gate)

A minimal, committed, mine-shaped fixture whose **parse output** is asserted to carry the head offset — the gate that must be green *before* any emit change. It exercises the full shape (head `+1` on an interior domain position + parameter offsets on the body tail) without needing the raw corpus (which is CI-absent).

**Fixture** `tests/fixtures/head_offset_ir_roundtrip.gms` (spec):

```gams
Set k /nw/, l /1*3/, i /1*2/, j /1*2/;
Parameter li(k) /nw 0/, lj(k) /nw 0/;
Set c(l,i,j); c(l,i,j) = yes;
Variable x(l,i,j), z;  Positive Variable x;  x.up(l,i,j) = 1;
Equation pr(k,l+1,i,j), def;
pr(k,l+1,i,j)$c(l,i,j)..  x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);   * head +1 on position l + body param offsets
def..                     z =e= sum((l,i,j), x(l,i,j));
Model m /all/;  Solve m maximizing z using lp;
```

**Assertions (parse → EquationDef, no emit):**

```python
eq = parse_model_file(fixture).equations["pr"]
assert eq.has_head_domain_offset is True
assert eq.domain == ("k", "l", "i", "j")                       # collapsed base
off = eq.head_domain_offsets
assert off[0] is None                                          # k: no head offset
assert isinstance(off[1], IndexOffset) and off[1].base == "l"  # l: the head offset
assert off[1].offset == Const(1.0) and off[1].circular is False
assert off[2] is None and off[3] is None                       # i, j: no head offset
# the param offsets remain in the body (already preserved today):
lhs = eq.lhs_rhs[0]   # x(l, i+li(k), j+lj(k))
assert any(isinstance(ix, IndexOffset) and isinstance(ix.offset, ParamRef) for ix in lhs.indices)
```

This is a **committed always-run** guard (mirrors the `tests/fixtures/crossterm_shapes/` pattern), so the IR-plumbing round-trip is protected independently of the raw corpus. It is the Phase-1 completion gate: **green here ⇒ proceed to Phase 2; red ⇒ the plumbing is wrong, do not touch emit.**

---

## 5. Phase-2 shared 3-site helper signature

Once `head_domain_offsets` is plumbed, a single helper computes the base↔head index correspondence, parameterized by (head δ from the IR field, parameter offsets from the body), so all three emit sites apply it identically. Sketch:

```python
def head_offset_index_map(eq_def: EquationDef) -> HeadOffsetMap:
    """The base<->head index correspondence for a head-domain-offset equation.
    Reads the head δ from eq_def.head_domain_offsets (Phase-1 IR field) and the
    tail parameter offsets from the equation body (lhs_rhs). Returns the mapping
    the three emit sites share so comp_pr / the dual transfer / stat_x agree on
    the l+1 / ±li / ±lj correspondence."""
    # head_delta: {position -> IndexOffset}  (e.g. {'l': +1})   <- from head_domain_offsets
    # tail_param_offsets: {position -> IndexOffset}             <- from lhs_rhs body VarRefs
    ...
```

**The three call sites (must apply the map atomically — all three or none):**

| Site | File:line | Role |
|---|---|---|
| Site 1 — `comp_pr` head var | `emit_gams.py:2951/:3125`, `equations.py:1072/:1103/:1173` | Emit the precedence body with the `l+1` head + `i+li(k)`/`j+lj(k)` tail — the site Day-7 proved still infeasible for the offset directions. |
| Site 2 — `--nlp-presolve` dual transfer | `emit_gams.py:_emit_nlp_presolve (:1354)` | Read `pr.m` at the `l+1` **head** (not base `l`) + drop `abs()` (sign-check vs the `nu`-class flip). Day-7: fixing this alone clears only the `nw` direction. |
| Site 3 — `stat_x` cross-term | `stationarity.py:_try_build_param_offset_crossterm (:5618)` | `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` — landed (#1224); must stay consistent with Sites 1–2 via the shared map. |

**Atomicity requirement:** the map must be applied to all three sites in one coordinated change. A partial application (e.g. Site 2 only) is the Day-7 failure mode — it clears `nw` (`li=lj=0`) but leaves `ne/se/sw` at ~1e10, i.e. an *inconsistent* LCP. The helper is the single source of truth so the three sites cannot drift.

---

## 6. Cold-INFES-by-direction success histogram (Phase-2 gate) + the 4th-site REPLAN exit

mine is a **convex LP** ⇒ a monotone LCP ⇒ **no Case-c escape**: a correct emit *must* cold-solve. So the Phase-2 completion gate is a per-k-direction infeasibility histogram driven to zero, then a cold MS 1.

**Baseline (Day-6, `ISSUE_1443`):** cold MS 5; `lam_pr`/`comp_pr` blow up to **~4.07e10 across all four k-directions**; the 38 `comp_pr` INFES rows partition **nw 6 / ne 9 / se 12 / sw 11**.

| Stage | nw (`li=lj=0`) | ne / se / sw (param offsets active) | verdict |
|---|---|---|---|
| Baseline (cold) | ~4.07e10 | ~4.07e10 | MS 5 |
| Site-2-only fix (Day-7 experiment) | → 0 | ~1e10 (still) | still MS 5 — **partial application is not enough** |
| **Shared 3-site helper (target)** | → 0 | **→ 0** | **cold MS 1**, `compare_objective_match` to the NLP |

**Gate (`scripts/diagnostics/kkt_residual.py`):** warm residual → 0 at the NLP optimum, then the *cold* LCP feasible (MS 1) with `x ≤ x.up = 1` (no `x → 4e10`) across **all four** k-directions.

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms --json /tmp/mine_headoffset.json
.venv/bin/python -m src.cli data/gamslib/raw/mine.gms -o /tmp/mine_mcp.gms --quiet \
  && gams /tmp/mine_mcp.gms lo=0 o=/tmp/mine_mcp.lst ScrDir=/tmp     # must reach MODEL STATUS 1
```

**4th-site REPLAN exit (→ Sprint 32).** The Day-4 cold trace listed 49 INFES across `comp_pr`, `comp_lo_x`, `comp_up_x`, `stat_x`, `def`. Day-6 attributed the driver to the 38 `comp_pr` rows, so the bound-complementarity rows (`comp_lo_x`/`comp_up_x` ⊥ `piL_x`/`piU_x`) are *hypothesized* to clear once `comp_pr` is consistent. **If, after the shared 3-site helper drives all four `comp_pr` directions to 0, the cold LCP is still infeasible with a residual localized to the bound rows** (`piU_x` never set because `x.up` is routed through `comp_up_x`), that is a genuine **4th site** — a deeper bound-complementarity architecture change beyond the 3-site map. → **REPLAN mine to a Sprint-32 head-offset-architecture-Phase-3 workstream**, reallocating the remaining budget per the Task-7 assessment (mine's +1 Solve becomes conditional; the IR plumbing + shared helper still land as reusable foundation). Because mine is convex, this is *still* an emit/index-map bug (Case-b), never a warm-start/non-convexity exit.

---

## 7. Unknowns resolved

- **1.1 (head-offset IR round-trip): ✅ VERIFIED — favorable.** The head offset is discarded at **parse** (`_domain_list_has_offset` → bool), not normalize; `NormalizedEquation` doesn't carry it and consumers read the original `EquationDef`. The fix is a **field addition** (`EquationDef.head_domain_offsets`, mirroring `declaration_domain`) + copy-through at the ~3 reconstructor sites — **not a deep normalize rewrite.** The param offsets are already preserved in the body. Round-trip unit reproduction specified (§4).
- **1.2 (shared helper vs 4th site): mine-only, 3 sites confirmed with a bounded 4th-site risk.** Once plumbed, one helper parameterized by (head δ, param offsets) drives Sites 1–3 (`comp_pr` / dual transfer / `stat_x`) atomically. The 4th-site risk (bound complementarity `comp_lo_x`/`comp_up_x`) is the explicit Sprint-32 REPLAN exit if it persists after the `comp_pr` fix (§6).
- **1.3 (cold-LCP consistency): hypothesis firm (convex LP ⇒ no Case-c).** The shared-helper `comp_pr` fix must drive the `x → 4e10` LCP residual to 0 across all four k-directions → cold MS 1. A residual after the 3-site fix is a remaining emit/index-map bug (still Case-b), never non-convexity — continue the trace / take the 4th-site exit, do not REPLAN to warm-start.
- **1.4 (IR blast radius): ✅ zero emit change from the field addition.** Populating `head_domain_offsets` is inert until a consumer reads it; the Phase-2 helper is gated to the param-offset shape (mine only). Head-offset *equations* are common (mine/robert/camshape/ramsey/abel in a 10-model sample) but the param-offset coupling is rare. Phase-1 verification = a full-corpus parse-scan + a golden byte-diff showing zero changes before Phase 2.

---

## Appendix — evidence

- **Empirical parse of `data/gamslib/raw/mine.gms`** (read-only): `pr.domain=('k','l','i','j')`, `pr.has_head_domain_offset=True`, `pr.lhs = x(l, i+li(k), j+lj(k))` (param offsets preserved as `IndexOffset`/`ParamRef`), `pr.rhs = x(l+1, i, j)` (the head `+1` survives only in the body), `pr.condition = SetMembershipTest(c,(l,i,j))`.
- **Code trace (read-only):** `_domain_list_has_offset` (`parser.py:932`, bool collapse) → `parser.py:3856/:3952`; `EquationDef` + `declaration_domain` precedent (`symbols.py:135/:144/:157`); `IndexOffset` (`ast.py:346`); `normalize_equation`/`NormalizedEquation` (`normalize.py:90/:13`, no head-offset field); reconstructor copy-through (`sqr_reformulation.py:88/:95/:108/:115`, `complementarity.py:242/:256`); Site 2 `_emit_nlp_presolve` (`emit_gams.py:1354`); Site 3 `_try_build_param_offset_crossterm` (`stationarity.py:5618/:5825`).
- **Head-offset corpus sample** (read-only parse): mine/robert/camshape/ramsey/abel carry head-offset equations; launch/otpop/trnsport/chenery/weapons do not.
- **Cold-INFES-by-direction** (`ISSUE_1443` Day-6/7): baseline ~4.07e10 across nw/ne/se/sw; Site-2-only clears `nw`, leaves `ne/se/sw` ~1e10.
- No `src/` or golden change; all probes were read-only parses.
