# Sprint 37 Day 4 — P2 ganges: Cascade + `rPower` Control → **REPLAN**

**Date:** 2026-08-11 · **Branch:** `planning/sprint37-day4-ganges-rpower` · **Scope:** control-only — all four fixes were applied as a scratch patch, measured, and **REVERTED**. `src/` is byte-identical to `main`; DB untouched.

**Verdict: 🔶 REPLAN — every fix works, and the cascade still cannot land.** All four take ganges *and* gangesx from `rc=2` (78 × `$141`, 3 × `$145`, 9 × `$149`) to **`rc=0`, zero `$NNN`, zero `rPower`**. The full-corpus leak gate then refused it: the `$149` rebind drifts **`prolog`**, a live `model_optimal` + match model, and `$149` **cannot be dropped** — without it ganges returns to `rc=2`. Filed as **#1668**.

---

## 1. The day's premise was wrong — the cascade is not on `main`

Day 4's prompt reads *"re-apply the verified cascade … then take `rPower` first"*, which presumes the cascade is in place. It is not. The first presolve run failed with the cascade's **first** root:

```
78 × $141      3 × $145      9 × $149      gams rc=2
```

`a8ff626c` is explicitly *"[WIP, not shipped]"*, and its helper `_expr_contains_varref_attr` has **zero** occurrences on `main`.

**Day 0's fingerprint check was a false positive, and it was mine.** It reported *"✓ `$141` helper `_expr_contains_varref_attribute` present"* — but that function came from `25feacd3`, *"Fix #881: cesam missing dollar conditions"*, an unrelated change with a near-identical name. Matching the string proved a *component* existed; I reported it as the *cascade* being in place.

This is the sprint's recurring error in a fourth form — verify a component, assert an end-to-end property. The prior three: `--resolve-changed` returning GO without markov in it (Day 2), the `determinism` marker matching a selector no job invoked (Day 3), and `dict.get()` unable to distinguish a removed key from a null one (Day 3).

## 2. All four fixes work — on both models, per-model, never inferred

| measurement | before | after |
|---|---|---|
| `$141` / `$145` / `$149` | 78 / 3 / 9 | **0 / 0 / 0** |
| `rPower` | `FUNC DOMAIN: x**y, x=0,y<0` | **gone** |
| `gams rc` | 2 | **0** |
| `EXECERROR` | 1 | **0 (cleared)** |
| deferred-bounds block before `$include` | present (line 500 vs `$include` 531) | **absent** |

Identical on **gangesx**, run independently.

### The 6th blocker is exactly where Task 5 put it

With `rPower` cleared:

| model | status |
|---|---|
| raw `ganges.gms` standalone | **MS-2 Locally Optimal @ 6395.5444** |
| embedded `ganges0` | **MS-5 Locally Infeasible @ −386785.5017** |
| `mcp_model` (PATH) | **MS-4 Infeasible** |

Matching the banked figure **to the decimal**. So this remains a **0-bucket** landing: ganges/gangesx would move `path_syntax_error` → `model_infeasible` — a *lateral* move, not a recovery. Solve stays 108, Match stays 93.

## 3. Two corrections applied mid-flight

**The `a8ff626c` patch is known-defective and I applied it verbatim.** PR #1617's review found its `_expr_contains_varref_attr` walks only `Expr.children()`, missing attributed `VarRef`s nested inside index expressions (e.g. an `.l` ref inside an `IndexOffset`) — so it can return `False` when it should return `True` and re-emit the very `$141` guard the skip exists to suppress. The Sprint-35 carryforward §4 **mandates** delegating to the existing `_expr_contains_varref_attribute`, which traverses indices properly. I caught this only by reading the carryforward *after* applying the patch, and corrected it (verified by direct call: positive on `adst(i) = dst.l(i)/2`, negative on a constant).

**My `rPower` gate crashed the emit.** I wrote `logger.info(...)`; `emit_gams.py` has no logger (it uses `warnings`). Cost one 2.5-minute emit cycle.

## 4. The leak gate — one benign drift, one blocking

```
Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 3 workers).
    EXPECTED DRIFT: ganges_mcp.gms (-925 bytes)
    EXPECTED DRIFT: gangesx_mcp.gms (-925 bytes)
    LEAK DRIFT: korcge_mcp_presolve.gms (-426 bytes)
    LEAK DRIFT: prolog_mcp.gms (-3 bytes)
  LEAK: 2 unexpected model(s) drifted: korcge, prolog
```

Both were **diagnosed, not assumed**.

### `korcge` — benign, and the fix correctly co-applies

The drift is entirely the `rPower` gate: **18 lines removed, 0 added**, all deferred bounds. Its statements *are* in the source (`er.fx`, `pindex.fx`, `k.fx(i)`, `mps.fx` each appear in `korcge.gms`), so the `$include` re-supplies them — the gate's premise holds. Verified by solving: still **`MODEL STATUS 1 Optimal`** at objective **339.2130**, exactly the DB's recorded match.

⇒ Not collateral damage; a second correct application. When this lands, `korcge` belongs in `--expect-drift`.

### `prolog` — blocking, and the reason is structural

The `$149` rebind rewrites the **variable** reference while leaving the **parameter** index untouched:

```
before:  p(gp) ** eta(g,gp,h)  *  eta(g,gp,h)  /  p(gp)  /  p(gp) ** eta(g,gp,h)
after:   p(g)  ** eta(g,gp,h)  *  eta(g,gp,h)  /  p(g)   /  p(g)  ** eta(g,gp,h)
                ^^^^^^^^^^^^^^                       exponent still indexes gp
```

pairing price `g` with exponent `eta(g,gp,h)`. And `gp` was **already bound** by the enclosing `sum(gp, …)`, so there was no free-index leak to repair — the rebind's own justifying comment (*"the emitter's aliasing will NOT rename it … so `j` leaks free"*) does not apply.

On ganges the same rebind **is** correct: `prod` over `j`, differentiate w.r.t. `pc(i)`, `j ≠ i`, and the emitter genuinely will not rename a sibling multiplicative factor.

prolog still solves `MODEL STATUS 1 Optimal`, but its objective is ~0 (`nlp = -0.0`, `mcp = -6.25e-13`), so the objective is a **weak** check — a degenerate value cannot distinguish a correct solution from a changed one. Under the byte-identical discipline, an unjustifiable change to a matching model's stationarity blocks the landing regardless.

## 5. `$149` is load-bearing — there is no leak-free subset

Reverting **only** the `$149` rebind (leaving `$141`/`$145` + the `rPower` gate applied):

```
gams rc=2      9 × $149
```

So the cascade cannot be split. The `rPower` gate is correct and verified but **unreachable in practice** until `$149` is narrowed.

## 6. A banked claim this corrects

`SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5 lists among the `$149` evidence: *"the full golden-staleness scan shows no non-collateral prod model drifts"*. Measured on current `main` + the cascade, **`prolog_mcp.gms` drifts**. That claim does not hold on this tree — which is precisely why the gate is run per-landing rather than trusted from the bank.

## 7. Disposition

- **`src/` reverted** — byte-identical to `main`; DB untouched. Zero broken code, the S30–S37 pattern.
- **#1667** (deferred-bounds ordering) → 🔶 **CONTROL VERIFIED, LANDING BLOCKED**. The fix is correct and measured on three models; it cannot ship alone.
- **#1668** (the `$149` rebind over-fire) → **filed**, with two concrete fix directions: rebind parameter indices consistently, or restrict the trigger to a genuinely-free prod bound. Direction 2 is closer to the original intent.
- **P2 remains 0-bucket for Sprint 37** regardless of #1668 — the 6th blocker (embedded MS-5 divergence) is untouched, so even a clean cascade buys a lateral `path_syntax_error → model_infeasible` move, not Solve or Match.
- **Day 5 (Checkpoint 1)** should record P2 as REPLAN'd and decide whether #1668's narrowing is worth the remaining P2 budget, given the bucket is 0 either way.

---

**Document Status:** ✅ Complete — Sprint 37 Day 4 (control PROCEED on the fix, REPLAN on the landing; `src/` reverted).
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 execution team
