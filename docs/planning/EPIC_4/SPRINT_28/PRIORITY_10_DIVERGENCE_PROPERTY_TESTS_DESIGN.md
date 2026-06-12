# Priority 10 — Embedded-NLP-Divergence Detector + AD Cross-Term Property-Test Catalog (Design)

**Task:** Sprint 28 Prep Task 8 (the detector + property tests are *built* in-sprint; this is the design + catalog)
**Date:** 2026-06-11
**Deliverable scripts (to be built):** `scripts/diagnostics/check_presolve_divergence.py` + a property-test suite under `tests/integration/emit/`
**Purpose:** Two systematic guards for the recurring Sprint 24–27 defect classes —
1. the **embedded-NLP-divergence** detector for the `$onMultiR` re-run bug class that drove #1378 (launch) and #1424 (camshape);
2. the **AD cross-term property-test catalog** for the offset/alias/parameter-valued-offset stationarity defects (#1224/#1388/#1390).

---

## Part 1 — Embedded-NLP-Divergence Detector (Unknown 10.1)

### The bug class

Under `--nlp-presolve`, the emitted MCP `$include`s the source NLP under `$onMultiR` and solves it (the warm-start pre-solve), then transfers its duals (`.m`) to the MCP multipliers. Because `$onMultiR` **re-runs the source statements**, any non-idempotent statement re-applies, so the *embedded* NLP can diverge from the *standalone* NLP:

- **#1378 launch** — a self-referential parameter assignment (`pre2('stage-3') = pre2('stage-3')*10**pre3(...)`) re-applied → embedded objective 2604.01 vs standalone 2257.80.
- **#1424 camshape** — `_emit_dynamic_subset_defaults` blanket-populated model-assigned subsets (`first/last/middle`) → embedded NLP infeasible (area=5.009) vs standalone optimum 4.2841.

Both were found mid-investigation; a translate-time detector would have flagged them at Day 0.

### How the detector extracts the two objectives (Unknown 10.1 Q1)

The presolve emit already sets the objective variable `.l` from the `$include`d NLP solve (e.g. `cost.l` in `launch_mcp_presolve.gms`, captured later as `nlp2mcp_obj_val = cost.l`). The detector:

1. **Standalone NLP objective** — solve `data/gamslib/raw/<model>.gms` directly (or reuse the committed `_NLP_REFERENCES` value); read the objective-variable `.l` from the listing.
2. **Embedded NLP objective** — emit the model with `--nlp-presolve`, then insert a probe `Display <objvar>.l;` (tagged, e.g. `EMBEDDED_NLP_OBJ`) **immediately after the `$offMulti`** that closes the `$include` block (post-include, *before* the dual transfer + the MCP `Solve`), run GAMS, and parse the tagged value from the listing. (Equivalently: run the presolve emit with the MCP `Solve` short-circuited and read `<objvar>.l`.)
3. **Compare** — flag when `|embedded − standalone| / max(1, |standalone|) > tol`, or when the embedded solve reports a worse model status (infeasible) than the standalone (the camshape case).

### Interface

```bash
.venv/bin/python scripts/diagnostics/check_presolve_divergence.py            # all presolve models; exit 1 on any unallowlisted divergence
.venv/bin/python scripts/diagnostics/check_presolve_divergence.py --model launch
.venv/bin/python scripts/diagnostics/check_presolve_divergence.py --tol 1e-4 --json out.json
```

| Flag | Meaning |
|---|---|
| (none) | check every `--nlp-presolve` model; exit non-zero on any non-allowlisted divergence |
| `--model <id>` | one model |
| `--tol <float>` | relative objective tolerance (default `1e-4` — looser than emit byte-tol; this is a *solver* comparison) |
| `--json <path>` | machine-readable divergence report |

### Tolerance (Unknown 10.1 Q2)

`tol = 1e-4` relative on the objective separates a real divergence (launch 2604 vs 2257 ≈ 13%; camshape infeasible) from NLP-solver numerical noise (two solves of the same model agree to ~1e-6). Model-status divergence (embedded infeasible, standalone optimal) is always flagged regardless of `tol`.

### False-positive allowlist

A model legitimately differs only if its source NLP is genuinely non-idempotent **by design** (rare). The allowlist (`scripts/diagnostics/presolve_divergence_allowlist.txt`, expected empty or near-empty at first) excludes such models with a documented reason; an allowlisted model that *stops* diverging is reported as a warning (stale allowlist).

### Validation against the past wins (Unknown 10.1 — Acceptance)

| Case | Pre-fix embedded obj | Standalone obj | Detector verdict |
|---|---|---|---|
| #1378 launch | 2604.01 | 2257.80 (~13% gap) | **FLAG** (relative gap ≫ tol) |
| #1424 camshape | infeasible (area=5.009 / MS≠1) | 4.2841 (MS 1) | **FLAG** (model-status divergence) |

Replaying the pre-fix emit for each (revert the #1378 `skip_self_ref_presolve` / the #1424 subset-default skip) must reproduce these flags — the in-sprint acceptance test.

### CI wiring

A `.github/workflows/` job (or a stage in the existing nightly) running the detector on the 11 presolve models; gate PRs touching `src/emit/original_symbols.py` / `src/emit/emit_gams.py` (the presolve emit path). Runtime is small (11 models, NLP solve only).

---

## Part 2 — AD Cross-Term Property-Test Catalog (Unknowns 10.2, 10.3)

Each recurring cross-term shape gets a **minimal synthetic GAMS model** (a few variables/equations) with a **hand-derived stationarity cross-term** the emit must produce. The property test emits the synthetic model (in-process, sub-second) and pattern-asserts the `stat_*` row contains the hand-derived term — turning the #1224/#1388/#1390 defect class into a systematic guard rather than ad-hoc per-model goldens.

### Catalog — 6 shapes (Unknown 10.2)

| # | Shape | Synthetic constraint | Hand-derived `stat_x` cross-term the emit must produce | Guards |
|---|---|---|---|---|
| 1 | **single-axis offset Sum** | `link(t).. x(t) =g= sum(tt$(ord(tt)=ord(t)+1), x(tt)) - 1` | `... + sum(tt, 1$(ord(t)=ord(tt)+1)*lam_link(tt)) - lam_link(t) ...` (offset **inverted**: `tt = t-1`) | general offset stationarity |
| 2 | **self-alias Sum** | `bal(i).. e(i) =e= sum(jj, a(i,jj)*x(jj))` (alias over the var's own set) | `stat_x(j): sum(i, a(i,j)*nu_bal(i))` (sum index → stat index `j`; eq index → alias `i`) | the consolidated-alias path (#1381) |
| 3 | **cross-set alias Sum** | `dem(i).. e(i) =g= sum(j, b(i,j)*x(j))` (distinct sets `i`,`j`) | `stat_x(j): sum(i, b(i,j)*lam_dem(i))` — **no `i↔j` swap** (the #1398 regression shape) | Pattern-C gate over-reach (#1398) |
| 4 | **parameter-valued offset** (#1224) | `pr(k,l,i,j).. x(l, i+li(k), j+lj(k)) =g= x(l+1,i,j)` | `stat_x(l,i,j): sum(k, lam_pr(k,l,i-li(k),j-lj(k))) - sum(k, lam_pr(k,l-1,i,j))` (param offset **inverted**) | #1224 mine |
| 5 | **interior+edge convex-combination** (#1388) | `convexity(middle(i)).. -r(i-1)*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cos =l= 0` (+ edge `convex_edge*`) | `stat_r(i)`: interior `(-r(i-1)-r(i+1))*lam_convexity(i)$(middle(i))` + `lam_convexity(i±1)` cross-terms guarded by **canonical `middle(i±1)`** (not the looser `ord` guards) | #1388 camshape |
| 6 | **tree-predicate-conditioned aliased Sum** (#1390) | `dembal(n).. e(n) =e= sum(nn$tree(nn,n), y(nn))` | `stat_y(n): sum(nn$tree(n,nn), nu_dembal(nn))` — tree predicate preserved (the **inverted** `tree(n,nn)`), single guarded Sum (not per-element enumeration) | #1390 kand |

Shapes 4/5/6 are the literal #1224/#1388/#1390 defect shapes (Acceptance Criterion: the defect class is explicitly represented); 1/2/3 are the foundational offset/alias/cross-set recurrences from the Sprint 24–27 history (#1381 consolidation, #1398 cross-set over-reach). The catalog is complete for the carryforward defect class; additional shapes (e.g. the `card(t)-ord(t)` time-reversal of #1335) can be appended as shape 7+ in-sprint.

**Prototype confirmation:** shape 1 was emitted from a minimal synthetic model — the emit produced `stat_x(t).. c(t) + sum(tt, 1$(ord(t) = ord(tt) + 1) * lam_link(tt)) - lam_link(t) - piL_x(t) =E= 0`, exactly the hand-derived inverted-offset form. Byte-identical on a re-emit.

### Property-test spec (Unknown 10.3)

- **Location:** `tests/integration/emit/test_ad_crossterm_shapes.py` (alongside the existing emit integration tests), marked **`@pytest.mark.integration`** — the tests read fixture `.gms` files and run the cross-module emit pipeline (I/O + cross-module), which matches the repo's `integration` marker, not `unit` ("Fast unit tests with no I/O"). They are still tiny and sub-second despite the marker.
- **Fixtures:** the 6 synthetic `.gms` models committed under `tests/fixtures/crossterm_shapes/` (small, hand-checkable, always-run — not gitignored like the GAMSlib corpus).
- **Assertion form:** emit the synthetic model **in-process** (the same emit API the existing emit tests use — not a subprocess), extract the target `stat_*` row, and **pattern-match** the hand-derived cross-term (normalize whitespace; assert the key sub-expression is present — e.g. `lam_link(tt)` guarded by `ord(t) = ord(tt) + 1`), robust to incidental re-parenthesization/reordering.
- **Speed (Unknown 10.3 Q1):** in-process emit of a tiny synthetic model is **sub-second** (the 4.38 s measured for a `python -m src.cli` subprocess is interpreter+import startup, not the emit; the in-process path the test suite already uses avoids it). The 6-test suite adds negligible CI time.
- **Byte-stability (Unknown 10.3 Q2):** confirmed determinism-clean (PR12) — the shape-1 prototype re-emitted byte-identical; the pattern-match assertion is additionally robust to formatting.
- **CI wiring:** the property tests run inside the existing `make test` (every PR via `ci.yml`) — no separate workflow needed. The synthetic fixtures are committed, so they run in `--fast` CI too (unlike the skip-if-absent GAMSlib goldens).

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md && echo present
grep -Ei 'check_presolve_divergence|property test|cross-term' docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md
grep -cE 'offset|alias|parameter-valued|interior|edge|tree' docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md
```
