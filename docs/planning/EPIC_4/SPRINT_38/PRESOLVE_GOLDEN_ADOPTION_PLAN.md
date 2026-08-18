# Sprint 38 Prep Task 6 — Presolve-Golden Adoption Plan & Runtime Impact (P4)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task6` · **Measured at:** `cc8acf6c` · **Scope:** measurement + design. No `src/`, DB or golden change.

**Verdict: 🔶 ADOPT IN TWO TIERS, NOT WHOLESALE.** The runtime is safe with room to spare, `--min-scope` can be made self-maintaining, and the review protocol produced a finding the prompt anticipated: **14 of the 36 would pin an emit that does not currently reproduce its NLP solution** — **7** `mismatch`, **6** `skipped`, and one `model_infeasible`. Those are exactly the "freeze a bug into the reference set" cases, and they should not be adopted on the same terms as the other 22.

---

## 1. Inventory — the 36, and why they split

Task 2 already established reproducibility (Unknown 4.1 ✅): a clean `--only-solve` from a scratch directory regenerates **exactly 36** presolve goldens (17 → 53; discovered 170 → 206), with **zero bucket moves**.

The interesting structure is that **the 36 are a different population from the existing 17.**

| set | members |
|---|---|
| **existing 17** | agreste · bearing · camshape · cclinpts · cesam · chain · fawley · korcge · launch · mathopt3 · otpop · polygon · ps2_f_s · ps2_s · ps3_s_gic · robustlp · rocket |
| **new 36** | see tiers below |

The existing 17 are dominated by models already carrying a presolve match or sitting in the `--resolve-changed` set. The new 36 are not — and that difference is what the review protocol has to act on.

### 1.1 Tier 1 — the presolve path is load-bearing for a match (22)

```
catmix    cpack     etamac    harker    hhfair    himmel16
irscge    like      lrgcge    marco     mathopt1  mathopt4
maxmin    mingamma  moncge    paperco   qsambal   sambal
stdcge    tforss    weapons   worst
```

Each is `model_optimal_presolve` **+ match**. The presolve emit is the artifact that *produces the recorded match*, so a golden for it guards something the KPI depends on. **These are the adoption's whole value** — they take presolve coverage from 17 to 39 against 153 cold.

### 1.2 Tier 2 — a presolve golden, but no presolve match (14)

| model | outcome | comparison |
|---|---|---|
| china, circle, imsl, lmp2, prodsp2, spatequ, trig | `model_optimal_presolve` | **mismatch** (7) |
| aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran | `model_optimal_presolve` | **skipped** (6) |
| **mine** | **`model_infeasible`** | `not_tested` |

**This is the hazard the task exists to catch, with concrete members.** Adopting these pins, as the reference, an emit that:

- **for the 7 `mismatch` models** — demonstrably does *not* reproduce the NLP solution. The golden would encode a known-wrong answer as "expected".
- **for the 6 `skipped` models** — was never compared at all, so there is no evidence either way.
- **for `mine`** — belongs to a model that does not solve (`model_infeasible`). A presolve golden here guards the emit of a failing model.

A golden's job is drift detection, not correctness certification, so pinning a wrong-but-stable emit is *defensible*. But it has a real cost: **when someone later fixes `circle`'s presolve emit, the gate flags it as drift**, and the reflex is `make regen-goldens` — which is precisely the laundering path the leak gate exists to prevent. Tier 2 therefore needs a *deliberate, per-model* justification, not a batch decision.

## 2. The review protocol

**"Reviewed" means checked against the model's *expected* presolve emit — not against the run that produced it.** Concretely, per golden:

1. **Provenance** — regenerated from a clean `--only-solve` **from a scratch directory** (never `git add -A` afterward; the S37 Day-9 incident swept 20 runtime artifacts including `decis.lic`).
2. **Structure** — contains the presolve warm-start block and its expected idioms: the marginal→multiplier `.l` assignments (`lam_*.l = abs(*.m)`, `nu_*.l = *.m`), and the **#1322 NA-guard** where the model has division-based parameter assignments. A presolve golden *without* the NA-guard on a model that needs it would freeze the pre-S37 `robustlp` defect.
3. **Agreement with the record** — the model's DB row must say what the golden implies. A `model_optimal_presolve` + `match` row and a presolve golden are consistent; a `mismatch` row and a presolve golden are *not*, and that mismatch must be justified explicitly (Tier 2).
4. **Determinism** — byte-stable across `PYTHONHASHSEED {0,1,42}`, like every other golden.

**Triage order:** Tier 1 first (22, load-bearing), Tier 2 second and individually (14).

**Rejection criterion:** a golden is **not adoptable** if it is non-reproducible, or if it is structurally missing an idiom its model requires (e.g. an absent NA-guard). **Exclusions are recorded in `scripts/sprint_audit/golden_staleness_allowlist.txt` with a one-line reason**, which is where the existing 7 exclusions already live — so the justification sits next to the mechanism rather than in a planning document.

**Recommendation:** adopt **Tier 1 (22) in Sprint 38**; put **Tier 2 (14) behind a per-model sign-off**, defaulting to *defer*. That takes in-scope 163 → **185** and discovered 170 → **192**, closing most of the coverage asymmetry (presolve 17 → 39) without pinning known-wrong emits.

## 3. Runtime — measured, and the local number is a trap

### 3.1 The measurement that matters is CI, not this machine

| | at 163 in-scope | note |
|---|---|---|
| **local** (3 workers, quiet) | **1578.9 s = 26.3 min** | **misleading** |
| **CI** (`ubuntu-latest`, 3 workers) | **11.9 – 12.9 min** | 29 real sweeps observed |

The local machine is **~2× slower than the runner** for this workload. Extrapolating from it would have produced a false alarm: 26.3 min → ~32 min projected, against a **`timeout-minutes: 25`** budget — i.e. "adoption blocks every PR." **That conclusion would have been wrong**, and only measuring the actual CI durations avoided it.

*(The ~0.1-minute runs in recent history are the **skip path** — the "Decide whether to run" gate short-circuits docs-only PRs. Only the 29 runs over 5 minutes are real sweeps.)*

### 3.2 Projection at the enlarged scope

The `--all` corpus download (~1 min) is fixed; only the sweep scales.

| scope | typical | worst observed | budget used | headroom |
|---|---|---|---|---|
| 163 (today) | 11.9 min | 12.9 min | 52 % | 12.1 min |
| **199** (both tiers) | **14.3 min** | **15.5 min** | **62 %** | **9.5 min** |
| **185** (Tier 1 only) | ~13.0 min | ~14.1 min | ~56 % | ~10.9 min |

**0 timeouts expected, and the 3-worker default holds.** Per-golden timeout risk is driven by slow-emit models, and **none of the known slow-emit class (ganges, gangesx, clearlak, turkpow, dinam) is among the 36** — the allowlist already carries that tail. No mitigation (worker count, nightly split) is required.

**One caveat worth stating:** at 199 the job uses **62 % of a 25-minute budget**. That is comfortable now, but the corpus only grows. **A follow-up should raise `timeout-minutes` or split the sweep before scope exceeds ~250**, rather than discovering it when a required check starts timing out.

## 4. `--min-scope` — derive it, but from the right source

Adoption moves discovered goldens 170 → **206** (Tier 1+2) or → **192** (Tier 1 only), so the hard-coded `--min-scope 170` would silently under-guard the moment the goldens land.

**Applied atomically with the adoption**, in the same change, so the assertion never lags the corpus. Confirmed it still fires on **discovery** — `discover_goldens()` drops any golden whose raw source is absent, and `--min-scope` is compared against that pre-narrowing count, which is exactly the property that makes it catch an under-provisioned corpus.

### 4.1 Deriving the value — and the trap in doing it naively

The prompt suggests deriving rather than hard-coding, per the "derive, don't quote" principle. **That is right, but only from an independent source.**

| candidate source | verdict |
|---|---|
| filesystem `ls data/gamslib/mcp/*_mcp*.gms` | ❌ **vacuous** — this is the same quantity `discover_goldens()` starts from, so the assertion would compare a number to itself and always pass. That is the *self-certification* defect this whole task is about, reappearing in the guard. |
| **`git ls-files data/gamslib/mcp/*.gms`** | ✅ **independent** — the git index knows how many goldens are *committed* regardless of whether their raw sources were provisioned, which is precisely the failure `--min-scope` exists to catch |

Both currently report **170**, so the substitution is verifiable as a no-op before the goldens land.

**Recommendation:** replace the hard-coded literal with a value derived from `git ls-files`, so the floor tracks the corpus automatically and the "raise it in the same change" discipline becomes unnecessary. If that is deferred, the literal must move **170 → 192** (Tier 1) or **→ 206** (both tiers) in the adoption commit itself.

## 5. Sequencing against P1 and P2

**P1's full-corpus gate must run at the OLD scope first.** P1 (ganges) asserts *"only ganges/gangesx drift, `prolog` byte-identical"*; adding 36 goldens mid-track changes the comparison set and would make a clean P1 result unattributable.

**Handoff:** P1 runs its gate at 163 → P1 lands → **then** P4 adopts and raises `--min-scope` in the same commit.

**Interaction with P2 (sarf), from Task 5:** sarf's new golden and P4's adoption both move the scope, and **the arithmetic is order-independent** — both orders end at the same place. With the Tier-1 recommendation the endpoint becomes **193 discovered / 186 in-scope** (170 + 22 + 1 sarf) rather than 207/200.

## 6. What this changes about the coverage asymmetry

| | cold | presolve | ratio |
|---|---|---|---|
| today | 153 | 17 | 9.0 : 1 |
| **Tier 1 adopted** | 153 | **39** | **3.9 : 1** |
| both tiers | 153 | 53 | 2.9 : 1 |

Tier 1 alone closes most of the gap. The remaining 14 buy ratio at the cost of pinning emits that do not currently reproduce their NLP solutions — a poor trade for a gate whose value is that its references are trustworthy.

## 7. Reproduction

```bash
# §3.1 — the local baseline (SLOW: ~26 min; and NOT the number that matters)
/usr/bin/time -p make check-goldens

# §3.1 — the number that DOES matter: real CI sweep durations
gh run list --workflow="Golden Staleness Check" --limit 60 \
  --json databaseId,conclusion,createdAt,updatedAt,headBranch
#   runs > 5 min are real sweeps; ~0.1 min runs are the skip path

# §4.1 — the two candidate sources for --min-scope
git ls-files 'data/gamslib/mcp/*.gms' | wc -l    # independent  -> 170
ls data/gamslib/mcp/*_mcp*.gms        | wc -l    # vacuous      -> 170

# §1 — the tier split
#   Tier 1 = the 36 ∩ (outcome_category == model_optimal_presolve AND comparison_status == match)
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 6. **4.2 ❌ WRONG** (14 of 36 would pin non-reproducing emits → two-tier adoption) · **4.3 ✅ VERIFIED** (CI 11.9–12.9 min at 163 → ~14.3–15.5 min at 199, 62 % of a 25-min budget; the local 26.3 min is a trap) · **4.4 ✅ VERIFIED** (derive from `git ls-files`, not the filesystem).
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team
