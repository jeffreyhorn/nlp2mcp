# P7 Infrastructure Catalog — Property Fixtures, Phase-0-Doc CI Enforcement, Genuine-Floor Tracking (Prep Task 10)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task10` · **Scope:** docs/analysis-only — prototypes built and measured in `/tmp`; **no `src/` change, no CI wiring landed** (the check is drafted here, wired in-sprint). Two docs/issues remediations landed (§2.4, §5.2).

**One line:** both banked P7 premises are **wrong in the same direction — the guards they specify would be silently inert**. The property fixtures, written as the bank specifies (`pytest.skip` when `data/gamslib/raw/<model>.gms` is absent), **never run in CI**: `ci.yml` provisions only 5 raw models and neither markov nor fawley is among them. And the Phase-0-doc check, written as the prompt specifies (`## Phase 0: Acceptance Gate` + 4 `###` subsections), **rejects `ISSUE_1110` and `ISSUE_1111` — the two Sprint-37 landings it exists to gate.** Both are fixed here: the fixtures are re-specified corpus-free (measured, both shapes reproduce in <1 s), and the two issue docs are restructured to the canonical form.

Reference: `SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md` §1–§3, `CONTRIBUTING.md` §392–447, `SPRINT_37/LEAK_HARNESS_DESIGN.md` (Task 3), `MARKOV_DISCRIMINATOR_DESIGN.md` §6 (Task 4), `FAWLEY_DISCRIMINATOR_REFRESH.md` §7 (Task 6), `BASELINE_RECONFIRMATION.md` (Task 2).

---

## 1. The banked fixture spec produces a guard that never runs in CI (Unknown 7.3)

`FIXTURE_AND_HARNESS_CATALOG.md` §1 specifies both fixtures as *"fast in-process … `pytest.skip` if `data/gamslib/raw/<model>.gms` absent (CI lacks raw)"*. The parenthetical is **false as stated**, and the correction inverts the conclusion.

### What CI actually provisions

| workflow | pytest selector | raw corpus provisioned |
|---|---|---|
| `ci.yml` (the `make test` lane, every PR) | `-m "not slow and not determinism"` | `download_gamslib_raw.sh **--fast**` → **exactly 5 models** |
| `nightly.yml` | `-m "slow and determinism"` | full corpus |
| `golden-staleness.yml` | (no pytest) | full corpus |

`tests/integration/determinism_fast_fixtures.txt` — the single manifest both `--fast` and the determinism parametrize read — contains **`chenery, abel, partssupply, ps2_f, himmel11`**. **Neither `markov` nor `fawley` is in it.**

⇒ A fixture guarded on `data/gamslib/raw/markov.gms` **skips on every CI run, forever.** It is a local-only guard wearing the costume of an inline `make test` guard.

### The same mechanism, already in production, explains "red since March"

S36 §3 diagnosed the existing `test_markov_stationarity_has_correction_term` as *"red since birth … a `slow` test doesn't run in the default `make test`"*. The mechanism is sharper than that:

- it is marked `[integration, slow]` — **not** `determinism`;
- `ci.yml` selects `not slow` → **excluded**;
- `nightly.yml` selects `slow **and** determinism` → **also excluded**.

**It runs in no CI lane at all** — and even if a lane selected it, `markov.gms` is absent, so it would skip. Two independent silencers. Replacing a `slow` guard with a `skip-if-absent` guard swaps one silencer for the other; it does not fix the class.

### The fix: corpus-free fixtures — measured, both shapes reproduce

The existing `test_markov_multi_pattern.py` docstring asserts the inline route is infeasible: *"a structure that's difficult to reproduce with an inline minimal fixture without also needing the full AD + KKT pipeline."* The premise is right and the conclusion is wrong — **the full AD+KKT pipeline is callable in-process** (`parse_model_text` → `normalize_model` → `compute_objective_gradient` / `compute_constraint_jacobian` → `assemble_kkt_system` → `build_stationarity_equations`), which is exactly what `tests/unit/kkt/test_stationarity_gradient_condition.py` already does.

**Built and measured this task** (`/tmp` prototypes, current `main`):

| synthetic | reproduces | scale | build time |
|---|---|---|---|
| markov `σ=sp` analogue (`\|s\|`=3, `\|i\|`=2, `pi(s,i,sp,j,sp)`) | the `CASE_B` collapsed emit — **15** spurious `s__kktN` offset groups, and `nu_constr(s,i)` **trapped inside** `sum((s__kkt16,j), …)` | real markov: 45 groups (`\|s\|`=8) | **0.61 s** |
| fawley subset-diagonal analogue (`cfq(cf)` ⊂ `cf`, `bq(c,cf)`, `pbal(cfq,m)`) | the over-count — `sum((cfq,m), ((-1)*char(c,m)) * nu_pbal(cfq,m))` with **no** `sameas` guard | real fawley: same shape, `cfq__` re-symbolised | **0.14 s** |

Both are **corpus-free, subprocess-free, deterministic, sub-second** — so they need no skip guard and run on every PR.

**Scale-down is safe** because both assertions are *structural*, not cardinal: neither asserts a group **count** (which does vary with `|s|`), only the presence/absence of the defective shape.

### 1.1 `shape_markov_diagonal_kronecker` — final spec

- **Placement:** `tests/unit/kkt/test_shape_markov_diagonal_kronecker.py`, `pytest.mark.unit`. No `slow`, no skip guard.
- **Model:** the inline synthetic above (verbatim in the prototype; ~18 lines of GAMS).
- **Fail-before (MEASURED, not assumed):** the diagonal multiplier `nu_constr(s,i)` — indexed by the stationarity equation's *own* head indices — is emitted **inside** `sum((s__kktN,j), …)`, i.e. summed over alias indices it does not depend on, multiplying it by `card(s)·card(j)`. Regex-confirmed present today.
- **Pass-after:** `nu_constr(s,i)` appears as a **bare additive term** outside any `sum(...)`, and the off-diagonal `σ=sp` contribution appears as a single sum whose coefficient no longer carries the Kronecker `1 -`.
- **Must NOT assert** the `s__kktN` group count (15 synthetic vs 45 real) — that is the scale-dependent quantity.

### 1.2 `shape_fawley_2d_second_index` — final spec

- **Placement:** `tests/unit/kkt/test_shape_fawley_2d_second_index.py`, `pytest.mark.unit`. No skip guard.
- **Fail-before (MEASURED):** `nu_pbal` is summed over the whole subset domain `cfq` with **no** `sameas` binding it to the variable's `cf` index.
- **Pass-after:** the term carries `$(sameas(cfq…, cf))`.
- **Suffix tolerance (a real difference from the raw model):** the synthetic emits the plain `cfq`, while real fawley emits the AD layer's re-symbolised **`cfq__`** (no alias collision exists in the synthetic to force the suffix). The assertion must match `cfq\w*`, not the literal `cfq__`. This is precisely the `__`-suffix blind spot that Task 6 identified as the likely cause of conjunct 2 under-firing — so the fixture must not re-introduce it.

### 1.3 Keep the raw-corpus integration test as a second tier

The corpus-free fixture asserts the shape; it does not assert that **real markov** emits it. Keep `test_markov_stationarity_has_correction_term` as the end-to-end backstop, but **retire the claim that it is a guard**: give it `determinism` alongside `slow` so `nightly.yml`'s `slow and determinism` selector actually reaches it, or accept explicitly in the catalog that it is a local-only check. Choosing neither is what produced five months of undetected red.

---

## 2. Phase-0-doc CI enforcement (Unknown 7.2)

### 2.1 The enforcement gap is real and quantified

Historic compliance, measured over merged PRs (`gh pr view --json files`, PR-level not commit-level):

| PR | emit files | Phase-0 issue doc | outcome under the check |
|---|---|---|---|
| **#1647** S36 P7 robustlp NA-guard | 1 | ✅ 1 (`ISSUE_1322`) | pass — **but the doc was added under review**, not before |
| **#1620** S35 turkey `$161` (`src/emit/original_symbols.py`) | 1 | ❌ 0 | **BLOCKED** |
| **#1596** S34 P4 sense-aware bound transfer (`src/emit/`) | 1 | ❌ 0 | **BLOCKED** |

**1 of 3 recent emit-touching PRs complied, and that one only after a reviewer asked.** Neither #1620 nor #1596 falls in CONTRIBUTING's exception scope (`scripts/`, `tests/`, `docs/`, `.github/`, `data/`) — both are genuine violations of the written rule. Enforcement is warranted, and emit PRs are rare enough (3 in the scanned window) that the check's cost is concentrated exactly where it matters.

At the **commit** level only 6 of the last 25 emit-touching commits carry an issue doc — which is why the check must evaluate **the PR's full changed-file set**, not individual commits. #1647 is the proof: the `src/` commit and the doc commit were different commits *of the same PR*, and PR-level evaluation gives the desired behaviour (red → author adds the doc → green).

### 2.2 The rule must be calibrated, not assumed — three variants measured

**The population is 21** — the docs in `docs/issues/` carrying a Phase-0 heading, discovered with a **prefix** heading match. That qualifier is itself the first calibration finding: anchoring the regex with `$` (`^## Phase 0: Acceptance Gate\s*$`) discovers only **20**, silently dropping **`ISSUE_1330`**, whose heading carries a parenthetical suffix (`… (Sprint 28 Prep Task 5 — Priority 6 camcge)`). A `$`-anchored check would call that doc "missing Phase 0" when it has one, so every figure below is measured over the full 21.

Rule variants, all against **pre-remediation** content (`HEAD~1`) so the two Sprint-37 docs are still in their original form:

| rule | passes | fails |
|---|---|---|
| **A** — exactly 4 `###` subsections | 20/21 | `ISSUE_1224` (**6** — the canonical 4 plus two narrative refresh sections) |
| **B** — the 4 canonical names, exactly and in order | 17/21 | `ISSUE_1224`, `ISSUE_1330` (suffixed subsection names — *"Expected Emit Pattern (hypothesis — PR24)"*), **`ISSUE_1110`**, **`ISSUE_1111`** |
| **C** — the 4 canonical names present (prefix-match), extras allowed | 19/21 | **`ISSUE_1110`**, **`ISSUE_1111`** |

Rule B fails `ISSUE_1330` for the same reason the `$`-anchor does, one level down: its *subsection* names also carry parenthetical suffixes. Prefix-matching must apply at both levels.

**Adopted: rule C** + prefix heading match. It reflects CONTRIBUTING's actual intent (*"must contain exactly these 4 subsections … verification grep matches the literal `### <name>` form"*) while tolerating the additional sections `ISSUE_1224` legitimately carries.

**CONTRIBUTING wording follow-up:** "must contain **exactly** these 4" is what produced the over-tight reading (the Task-6 PR demoted a heading to `####` to preserve a count of 4). Recommend rewording to "must contain **these 4** … additional `###` subsections are permitted" when the check lands, so the doc and the gate agree.

### 2.3 The check — trigger, resolution, failure message

**Trigger** — mirror `golden-staleness.yml`, which is already correctly scoped:

```yaml
on:
  pull_request:
    branches: [main]
    paths:
      - "src/ad/**/*.py"
      - "src/kkt/**/*.py"
      - "src/emit/**/*.py"
```

Note this is **narrower than the leak gate**, which also arms on `src/ir/**`. That is intentional and matches CONTRIBUTING §392: the Phase-0 rule names `src/{ad,kkt,emit}` only. Do not widen them to match.

**Which issue doc?** Two accepted forms, either sufficient:
1. the PR changes a `docs/issues/ISSUE_*.md` that satisfies rule C; **or**
2. the PR **body** names an issue (`ISSUE_<N>` or `#<N>`) resolving to an existing `docs/issues/ISSUE_<N>_*.md` that satisfies rule C — CONTRIBUTING already requires the PR description to reference the Phase-0 PROCEED signal, so this adds no new authoring burden and lets a follow-on fix cite a doc that landed earlier.

**Escape hatch:** a `skip-phase0` label, mirroring `skip-golden-staleness`, for the exception-scope cases CONTRIBUTING contemplates (follow-on cleanup that doesn't change emit shape). Labels are visible in review, so the exemption is auditable rather than silent.

**Failure message** (points at the rule, the specific defect, and the fix):

```
Phase-0 acceptance gate MISSING for an emit-touching PR.

This PR changes src/{ad,kkt,emit}, which CONTRIBUTING.md §392-447 requires to
carry a Phase-0 acceptance gate BEFORE the src/ commit lands.

  changed emit files : src/kkt/stationarity.py
  issue docs checked : docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md
  defect             : missing required subsection(s):
                         ### Hand-Derived KKT Shape
                         ### Expected Emit Pattern

Add a `## Phase 0: Acceptance Gate` section with these 4 `### ` subsections:
  ### Hand-Derived KKT Shape       ### Expected Emit Pattern
  ### Verification Methodology     ### PROCEED/REPLAN Signal
(additional subsections are allowed). Format reference: docs/issues/ISSUE_1356_*.md

If this PR is exception-scope (no emit-shape change), apply the `skip-phase0`
label and say why in the PR description.
```

**Hook:** CI job only, **not** pre-commit. The S36 robustlp lesson is that the doc was needed *under review*; a pre-commit hook fires before the author knows the fix surface, which is exactly what PR24 forbids (the Day-0 trace establishes the surface, and `### PROCEED/REPLAN Signal` must cite it). Blocking the commit would incentivise authoring the doc from the prep-doc hypothesis — the failure mode PR24 exists to prevent.

**Reference implementation** (measured: passes 19, fails 2 — exactly `ISSUE_1110`/`ISSUE_1111` pre-remediation):

```python
REQUIRED = ["Hand-Derived KKT Shape", "Expected Emit Pattern",
            "Verification Methodology", "PROCEED/REPLAN Signal"]
PHASE0 = re.compile(r"^## Phase 0: Acceptance Gate\b", re.M)   # prefix — ISSUE_1330 has a suffix

def phase0_subsections(text):
    m = PHASE0.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return re.findall(r"^### (.+)$", rest[:nxt.start()] if nxt else rest, re.M)

def missing(text):                      # [] == conforming
    subs = phase0_subsections(text)
    if subs is None:
        return REQUIRED
    return [r for r in REQUIRED if not any(h.strip().startswith(r) for h in subs)]
```

### 2.4 Remediation landed: the check would have blocked its own sprint

`ISSUE_1110` (markov, Task 4) and `ISSUE_1111` (fawley, Task 6) use a **criteria-based** decomposition — `Correctness` / `Bucket & KPI` / `Leak-freedom` / `Regression guard` — not the canonical four. Both are the Phase-0 docs for Sprint 37's two P1/P4 landings. Landing the check without fixing them would have made Sprint 37's first emit PR red on its own gate.

A rename would have been wrong: the canonical sections carry *different content* (a hand-derived Lagrangian; an expected emit pattern), and auditing them surfaced a substantive omission — **neither doc carried the `Traced Fix-Surface (Day-0)` line that CONTRIBUTING §447 makes mandatory**, even though Tasks 4 and 6 both established the surface by tracing (`_add_indexed_jacobian_terms` `:6136–6158`/`:7214+` for markov; the disjoint-by-NAME branch `:7069–7096` for fawley).

**Both docs restructured here:** the canonical four added with their proper content (the hand-derivation, the expected emit pattern, the verification commands, and a PROCEED/REPLAN signal carrying the traced `file:line`), with the existing acceptance criteria retained as additional `###` subsections under rule C. Both now pass the check — verified.

---

## 3. The composed emit-PR gate (for the Task-11 schedule)

The three instruments are **complementary, not overlapping** — each catches a class the others cannot:

| # | gate | catches | cost | when |
|---|---|---|---|---|
| 1 | **Phase-0 doc check** (§2, to wire) | shipping without a hand-derived acceptance target | seconds | PR open, `src/{ad,kkt,emit}` |
| 2 | **Property fixtures** (§1, to land with each fix) | the *intended* model's shape silently regressing later | <1 s each | every `make test` |
| 3 | **`make leak-check MODEL=<id>`** (Task 3, on `main`) | the change perturbing the *other* 162 goldens | ~25 min | PR + pre-land |

Ordering within a landing day: **Phase-0 doc → src change → fixture green → `leak-check` → land.** Gate 1 is authored before the fix, gate 2 fails-before/passes-after it, gate 3 runs on the finished emit.

**Per-track gate assignment** (note two tracks invert the standard recipe):

| track | fixture | leak gate | note |
|---|---|---|---|
| **P1 markov** | `shape_markov_diagonal_kronecker` | `make leak-check MODEL=markov` | the standard recipe |
| **P4 fawley** | `shape_fawley_2d_second_index` | `make leak-check MODEL=fawley` | **currently FAILS** (`dinam`, `shale` — Task 6 §3); must pass unqualified before landing |
| **P5 sarf** | none specified | **`make check-goldens`** — zero drift across 163 | **inverted**: sarf has no golden, so `--expect-drift sarf` reports `NO-OP` and fails for a non-correctness reason (Task 7 §4) |
| **P2 ganges** | none specified | `make leak-check MODEL=ganges,gangesx` | `$149` `_diff_prod` is a *general* AD fix — the widest blast radius of any S37 change; the leak gate is the whole safety argument |

**Land order (structural, not preference):** markov before fawley. They are alternative branches of the same `if/elif` chain (`_did_dim_mismatch_alias_fix`, set `True` at `:6925`; fawley's branch is `elif not …` at `:7060`), so a term taking markov's path cannot reach fawley's. Landing markov first means fawley's leak-check runs against a tree already carrying markov, which is the configuration that must actually be proven clean.

**Gap this composition does not close:** `golden-staleness` is still **not a required status check** (`required_status_checks.contexts` = `[]` — Task 3). Until a maintainer sets branch protection, all three gates are advisory: a PR can merge red. Wiring the Phase-0 check adds a *fourth* advisory gate, not a fourth blocking one. **This is the single highest-leverage P7 action and it is not a code change** — it is one branch-protection setting, and it is owner-assigned.

---

## 4. Genuine-floor tracking (Unknown 7.4 — re-confirmed)

Task 2 verified the PR25 recompute at S37 open; this task re-confirms it against the committed DB and specifies the bookkeeping.

**Anchor (unchanged, DB byte-identical to `78ceaead`):** 142 convex candidates → **Solve 108 · Match 93 = 63 cold-optimal + 30 presolve · genuine floor 75 · Translate 135**.

**The markov +1 is real, not a double-count.** markov sits in the **30-model presolve-match (methodology) partition** — `model_optimal_presolve` + match + `verified_convex`. A methodology match means the *cold* emit is byte-identical to pre-fix and the match exists only via warm-start. The P1 fix changes the cold emit, so if markov cold-solves to `MODEL STATUS 1` at `pvcost = 2401.577`, it leaves the methodology partition and enters the genuine floor:

**floor 75 → 76 · Match 93 unchanged · presolve-match 30 → 29 · cold-optimal 63 → 64.**

The Match total does **not** move — markov already counts. Only the genuine/methodology split moves. Reporting the markov landing as "+1 Match" would be wrong; it is **+1 genuine floor** and a partition transfer.

**Recording rule at S37 close:** the floor advances **only** on an emit-changing cold match (`modelstat` asserted from the solve listing, never inferred). If markov lands but PATH still needs the presolve warm-start to converge cold, the model stays methodology and the floor stays 75 — the S30 §3 / S31 §3 conditionality lesson, which has held flat at 75 for four consecutive sprints.

**Other S37 tracks and the floor:** fawley 0-bucket by construction (H-b, MS-5); sarf +1 Translate only; ganges +2 Solve or 0; turkey license-gated. **markov is the only track that can move the floor** — the same conclusion three prep tasks reached independently.

---

## 5. Epic-4 `SUMMARY.md` row-37

### 5.1 The row existed — with the wrong sprint's theme

`SUMMARY.md` row 37 read **"v2.0.0 release & Epic 5 planning (camcge dual-consistent Walras)"**. That is now **Sprint 40**'s theme (`PROJECT_PLAN.md:2096`). PR #1651 inserted the new Sprint 37 and renumbered old S37/38/39 → S38/39/40 across `PROJECT_PLAN.md`, but **the sweep did not reach `SUMMARY.md`** — so the epic's at-a-glance table pointed the next three sprints at the wrong work, and rows 38–40 did not exist at all.

This is the **third** instance this prep cycle of the same failure mode — a finding that lives in one document and never reaches the document someone will actually use (Task 9 found it in the rocket send checkbox and in the Epic-5 handoff spec). It is not a documentation-hygiene nit; it is the recurring structural defect of this planning system.

**Fixed here:** row 37 retitled to the real Sprint-37 theme, and rows 38/39/40 added from `PROJECT_PLAN.md:1926/2009/2096`.

### 5.2 Row-37 skeleton (fill at S37 close)

```
| 37 | 39–40 | S36 carryforward — markov σ=sp +1-floor lever, ganges/gangesx ≥5-blocker
  recovery, rocket/mine/camcge consultation & Epic-5 cycle, fawley & sarf, turkey +
  GAMS-54 re-baseline | Solve <108|110> / Match <93> / floor **<75|76>** …
  | <firm landings> | <REPLAN'd → S38> |
```

**Pre-registered fill rules** (so the row is written from the gates, not from narrative):

- **Headline KPIs** — from the S37-close `--resolve-changed` checkpoint + determinism ×3 `{0,1,42}`; state the DB byte-status explicitly (every sprint since S33 has been byte-unchanged, and saying so is what makes "flat" a measurement rather than an absence).
- **Floor** — 76 **only** if markov cold-matches with `modelstat` asserted; otherwise 75 with the methodology partition still at 30.
- **Firm landings** — a track counts as firm only if it passed all three §3 gates. A correctness fix that never passed its leak gate is a **carryforward**, not a landing (fawley is the live candidate for exactly this mislabelling).
- **Carryforwards** — carry the *bounded next step*, not the track name: the banked-diagnosis pipeline is the epic's most reliably valuable output, and its value is entirely in the specificity.

---

## 6. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **7.2** where the Phase-0-doc CI check hooks (the changed-path glob) | ✅ **VERIFIED — with two corrections** | §2 — trigger = `src/{ad,kkt,emit}/**/*.py` (**narrower** than the leak gate's, which also arms on `src/ir/**`; CONTRIBUTING §392 names only the three). Doc resolution must be **PR-level** (6/25 emit *commits* carry a doc, but the #1647 doc landed in a later commit of the same PR); accept a changed conforming doc **or** a PR-body `ISSUE_<N>` reference; `skip-phase0` label as the auditable escape hatch; **CI job, not pre-commit** (PR24: the surface isn't known at commit time). **Correction 1:** the rule must be *4 canonical names present, extras allowed* + a **prefix** heading match — measured, `exactly-4` fails `ISSUE_1224` (6 headings) and `$`-anchoring drops `ISSUE_1330` (suffixed heading). **Correction 2:** as specified it **rejects `ISSUE_1110` and `ISSUE_1111`** — Sprint 37's own P1/P4 Phase-0 docs; both restructured here (and both were missing the mandatory `Traced Fix-Surface (Day-0)` line). Compliance measured: **1 of 3** recent emit PRs complied, that one only under review. |
| **7.3** the property fixtures fail-before/pass-after and skip-if-absent | ❌ **WRONG (refuted) — "skip-if-absent" makes them inert in CI; re-specified corpus-free** | §1 — `ci.yml` provisions **5** raw models (`chenery, abel, partssupply, ps2_f, himmel11`); **neither markov nor fawley**, so a skip-guarded fixture **skips on every CI run**. The existing markov integration test is worse still: `[integration, slow]` is excluded by `ci.yml` (`not slow`) **and** by `nightly.yml` (`slow and determinism`) ⇒ it runs in **no** lane. **Both shapes reproduce corpus-free and in-process** — measured on current `main`: markov analogue **0.61 s** (15 spurious `s__kktN` groups; `nu_constr(s,i)` trapped inside a sum) and fawley analogue **0.14 s** (`nu_pbal` summed over `cfq` with no `sameas`), refuting the existing test's "difficult to reproduce with an inline minimal fixture" docstring. Fail-before confirmed by regex on both. Fixtures re-specified: `tests/unit/kkt/`, `pytest.mark.unit`, **no skip guard**, structural assertions only (never the `s__kktN` count — 15 synthetic vs 45 real), `cfq\w*` suffix-tolerant. |
| **7.4** the genuine-floor tracking holds at anchor 75 at S37 open | ✅ **VERIFIED (re-confirmed) — plus a stale-SUMMARY defect fixed** | §4 — DB byte-identical to `78ceaead` ⇒ **Solve 108 / Match 93 (63+30) / floor 75**; markov ∈ the 30-model methodology partition ⇒ the lever is a **true +1 floor** (75→76) with **Match unchanged at 93** (partition transfer: presolve-match 30→29, cold-optimal 63→64) — reporting it as "+1 Match" would be wrong. markov is the only S37 track that can move the floor. §5 — **defect found:** `SUMMARY.md` row 37 still carried the *pre-renumbering* theme ("v2.0.0 release & Epic 5 planning" — now Sprint **40**), because PR #1651's renumbering swept `PROJECT_PLAN.md` but not `SUMMARY.md`, and rows 38–40 were absent. **Fixed here**; row-37 skeleton drafted with pre-registered fill rules. |

---

## 7. Go / No-Go

**GO — P7's three instruments compose, with two premises corrected and one action that only the owner can take.**

- The property fixtures are **re-specified corpus-free and verified fail-before** — they will actually run, which the banked spec would not have.
- The Phase-0 check is **calibrated against the real corpus** and its two blocking-defects (the rule variant, and Sprint 37's own non-conforming docs) are fixed **before** the check lands rather than after.
- The genuine-floor bookkeeping is re-confirmed at 75 with markov the sole lever.

**REPLAN triggers:** the corpus-free markov synthetic stops reproducing the `CASE_B` shape once P1 lands its discriminator (expected — that *is* pass-after; but if the synthetic no longer reaches the discriminator's gate at all, the fixture is testing nothing and must be re-derived against the real model); the Phase-0 check false-fires on an exception-scope PR more than once (→ widen the escape hatch rather than loosen the rule).

**Owner-assigned, not schedulable:** make `golden-staleness` (and, once wired, `phase-0-gate`) **required** status checks. Until then every gate here is advisory and a red PR can merge.

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 10 (P7 infrastructure catalog).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team
