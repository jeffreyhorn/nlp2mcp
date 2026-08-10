# Full-Corpus Leak-Verification Harness — Design & Stand-Up (Prep Task 3)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task3` · **Scope:** `scripts/` + `Makefile` (the `--expect-drift` leak gate) + this design doc.

**One line:** the full-corpus staleness gate **already existed** (`golden-staleness.yml`, all 163 goldens, right trigger paths) — so the Sprint-36 markov leak was *not* caused by a missing sweep. The real gap is that the gate answers **"did anything drift?"** when a shared-function change needs **"did *exactly* the intended model drift?"** — and its remediation path (`make regen-goldens`) **launders a leak into the goldens**. This task closes that with `--expect-drift` / `make leak-check MODEL=<id>`, verified against 4 simulated scenarios.

---

## 1. Empirical correction to the prep assumption

The prep framing (`PREP_PLAN.md` Task 3, from `SPRINT_36/SPRINT_RETROSPECTIVE.md` §4) was *"ship a full-corpus mode as a required gate — the 6-model cohort is not the risk set."* Reproducing the actual state of the tree corrects this in three ways:

| Prep assumption | Measured reality |
|---|---|
| A full-corpus (163) mode needs to be built | **It already exists.** `.github/workflows/golden-staleness.yml` runs `check_golden_staleness.py` with **no `--models` restriction** → all 163 in-scope goldens, 25-min timeout, on every PR touching `src/{ad,kkt,emit,ir}/**`. |
| The trigger must be narrowed to `_add_indexed_jacobian_terms`-relevant changes | **The existing path trigger is already correct** — both shared functions live in `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms:5861`, `_compute_index_offset_key:4969`), covered by `src/kkt/**/*.py`. Narrowing to *function* scope would be strictly worse: fragile to refactors, and **any** emit-path change can drift goldens, so path-level is the right granularity. |
| The gate is the missing safety net | **The gate is not `required`** (`branches/main/protection` → `required_status_checks.contexts` = `[]` — *no* required checks are configured), **and** it only fires at PR time on `src/` changes. The S36 Day-2 markov leak was found during a **local `/tmp` control** whose prototype was reverted and never committed, so no PR ever existed for CI to gate. |

**So the failure mode was never "no sweep."** It was: (a) during the *control* phase there was no full-corpus instrument (a 6-model cohort was used by hand), and (b) even at PR time the gate's verdict is binary — see §2.

## 2. The real gap: the gate launders leaks

`check_golden_staleness.py` reports drift and prints:

> `Run `make regen-goldens` and commit the refreshed goldens (or, if unintended, fix the emit).`

and `--fix` (= `make regen-goldens`) refreshes **every** drifted golden indiscriminately (`check_one(..., fix=args.fix)` for all in-scope models). Trace the S36 markov scenario through it:

1. The markov `σ=sp` fix lands in `_add_indexed_jacobian_terms`. It is correct for markov and **leaks onto cesam/ferts/sroute**.
2. The gate fires: **4 goldens drifted** → red.
3. The author follows the printed advice: `make regen-goldens` → **all 4 goldens rewritten**, including the three leaked ones.
4. Commit the "refreshed goldens" → **gate green**. The leak is now the committed baseline, invisible forever after.

The binary verdict cannot distinguish *"my intended model changed"* from *"my change escaped its blast radius."* That distinction is the entire question a shared-function change needs answered — and it is what P1 (markov) and P4 (fawley) must gate on.

## 3. The fix: `--expect-drift` (the leak gate)

Turns the checker from *"did anything drift?"* into *"did **exactly** the intended set drift?"*

```bash
make leak-check MODEL=markov            # the P1 Phase-0 gate
make leak-check MODEL=fawley            # the P4 Phase-0 gate
make leak-check MODEL=markov,fawley     # both landed together
# underlying:
python scripts/sprint_audit/check_golden_staleness.py --expect-drift markov
```

**Verdicts** (exit 0 only on the first):

| Outcome | Meaning | Exit |
|---|---|---|
| `LEAK GATE PASS` | exactly the expected model(s) drifted; every other in-scope golden byte-identical | 0 |
| `LEAK: <models>` | an **unexpected** model drifted — the change escaped its target | 1 |
| `NO-OP: <models>` | an expected model **did not** drift — the fix didn't change the emit | 1 |
| `UNVERIFIED: N` | goldens timed out — the leak claim is **inconclusive** (not "clean") | 1 |

Three properties matter:

- **Anti-laundering.** Under `--expect-drift`, `--fix` refreshes **only** the expected models (`args.fix and (not expected or mid in expected)`). An unexpected drift is a leak to surface, never a golden to rewrite. The failure message explicitly says *"do NOT run `make regen-goldens` (that would launder the leak into the goldens)."*
- **No-op detection.** A "clean" sweep is a **failure** when you asserted your fix changes an emit — this catches a predicate that never fires (the fix silently doing nothing), which a binary gate reports as success.
- **Unverified ≠ clean.** A timed-out golden was never compared, so it cannot support a leak claim. `--expect-drift` treats timeouts as blocking (escape hatch: `--allow-unverified`, documented as voiding the claim). This is deliberately stricter than the base gate, where a timeout is a soft "couldn't verify in budget."
- **No silently-degraded claim.** An empty `--expect-drift` value (`--expect-drift ,`) is **rejected (exit 2)** — it would otherwise disable the gate *and* leave `--fix` unrestricted, i.e. plain laundering under a leak-gate command line. And because a `--models` sweep cannot see drift outside its subset, that combination is labelled `LEAK GATE PASS (SUBSET … — NOT a full-corpus leak claim)` with a warning, and records `"leak_claim_scope": "subset"` in the JSON report, so a scoped run can never be pasted as the Phase-0 evidence.

### Verified behaviour (4 simulated scenarios, this branch)

Drift was simulated by perturbing committed goldens (regen ≠ golden), then `git checkout --` restored them; the corpus is verified clean afterwards. Scenarios A–C used the **markov + cesam** pair (the real S36 shape); scenario D re-ran the same logic on the **rbrock + trig** pair because `--fix` re-emits each drifted golden twice for its determinism guard and cesam's emit is too slow for that double pass.

| Scenario | Setup | Result | Exit |
|---|---|---|---|
| **A — no-op fix** | clean tree, `--expect-drift markov` | `NO-OP: expected drift on markov but the emit was byte-identical` | 1 ✓ |
| **B — clean landing** | markov perturbed, `--expect-drift markov` | `LEAK GATE PASS: exactly the expected model(s) drifted (markov)` | 0 ✓ |
| **C — leak** | markov + cesam perturbed, `--expect-drift markov` | `LEAK DRIFT: cesam_mcp.gms` + `LEAK: 1 unexpected model(s) drifted: cesam` | 1 ✓ |
| **D — anti-laundering** | **rbrock + trig** perturbed, `--expect-drift rbrock` **with `--fix`** | `EXPECTED DRIFT: rbrock_mcp.gms` refreshed; **`LEAK DRIFT: trig_mcp.gms` left byte-untouched** | 1 ✓ |

Scenario D is the one that would have caught Sprint 36: the leaked golden is left dirty and named, so it cannot be silently absorbed.

**Scope note.** These scenarios were run with `--models` to isolate the logic on a fast pair. Because a `--models` sweep cannot see drift outside its subset, the tool now labels that combination explicitly — `LEAK GATE PASS (SUBSET of N golden(s) — NOT a full-corpus leak claim)` plus a warning — so a scoped run can never be mistaken for the Phase-0 full-corpus claim. An empty `--expect-drift` value is rejected outright (exit 2): it would otherwise disable the gate while leaving `--fix` unrestricted, i.e. silent laundering.

## 4. Cost inventory & the two modes

**Corpus shape** (measured on this branch via `discover_goldens()`):

| | count |
|---|---|
| goldens discovered (raw source present) | **170** |
| **in-scope** (gated) | **163** |
| allowlisted (out of scope / cross-platform) | 7 — `danwolfe, decomp, indus, nemhaus, nonsharp, saras, trnspwl` |
| total in-scope golden bytes | 1.9 MiB · median golden **6.0 KiB** |

**The emit-cost tail** (golden size is the reliable proxy — emit cost tracks model size, and the S36 measurements pin the extremes):

| Band | Models | Evidence |
|---|---|---|
| **Slow tail** (minutes each) | `turkpow` (159 KiB), `egypt` (84), `ferts` (80), **`ganges` (78)**, **`gangesx` (77)**, `turkey` (71), `dyncge` (39), `dinam` (38), `camcge` (35), `clearlak` (30) | ganges/gangesx measured at **~335 s** per emit (S36 Day-8 / Task-5 refs) — these dominate the sweep's wall clock |
| **Fast body** (sub-second to seconds) | the remaining ~150, median 6.0 KiB (smallest: `rbrock`, `trig`, `mathopt2` ≈ 3 KiB) | the 6-worker pool absorbs these while the tail runs |

**Measured aggregate budget** (the number that actually governs the design):

- **Local full sweep: ~7–8 min wall clock**, 163 goldens, 6 workers, **0 drifted / 0 failed / 0 timed out** (Prep Task 2, clean machine — `BASELINE_RECONFIRMATION.md` §4).
- **CI full sweep: green inside the existing 25-min ceiling** on every triggering PR (S35 Day-6, S36 Day-10 runs).

> **Note on method.** A per-model profiling sweep was attempted twice on this branch but the host carried heavy external load (load avg 26–97, 22 sessions), which made fine-grained per-model timings unreliable; it was abandoned rather than reported as precise. It is not load-bearing: the design question is the *aggregate* budget (measured above, twice), and the recommendation is to keep the sweep whole — so a fast/medium/slow partition is never used to select a subset.

**Mode design:**

| Mode | Scope | Trigger | Budget |
|---|---|---|---|
| **PR gate** (exists) | all 163 in-scope goldens | PR touching `src/{ad,kkt,emit,ir}/**` or the checker/allowlist | 25-min CI ceiling (currently passing) |
| **Leak gate** (new) | all 163, `--expect-drift <model>` | **manual/Phase-0**, run by the author *before* the `src/` commit — and re-run in the PR | same sweep, one extra assertion |
| **Nightly full** (exists, adjacent) | determinism sweep | `nightly.yml` cron, 360-min ceiling | already provisioned for the slow tail |

**The fast/nightly split the prep doc anticipated is not needed on the evidence**: the full sweep already completes inside the existing 25-min CI ceiling and has been green on every triggering PR (S35 Day-6, S36 Day-10 runs). Splitting into a fast subset would *reintroduce* the exact cohort-incompleteness that caused the S36 miss. **Recommendation: keep the sweep whole.** If the slow tail (ganges/gangesx) ever pushes past the ceiling, raise the timeout or move the tail to the existing `nightly.yml`, rather than shrinking the PR cohort.

## 5. Remaining gap for P7 (in-sprint wiring)

The gate is stood up and usable *now* (`make leak-check`). Two items remain for P7 in-sprint, both deliberately out of scope for a prep task:

1. **Make `golden-staleness` a required status check.** `required_status_checks.contexts` is `[]` today, so a PR can merge with the gate red or skipped. This is a repo-settings change (branch protection), not a code change — it needs the maintainer.
2. **Wire `leak-check` into the emit-PR template / CONTRIBUTING Phase-0 rule**, so a shared-function PR must paste its `LEAK GATE PASS` line — pairing with the Phase-0-doc CI check (Task 10 / Unknown 7.2).

## 6. What Tasks 4 and 6 now cite

Both Phase-0 acceptance gates can now reference a **real, tested invocation**:

- **Task 4 (markov P1):** `make leak-check MODEL=markov` → must print `LEAK GATE PASS`, proving cesam/ferts/sroute (and the other 159) are byte-identical. This is the instrument the 6-model cohort lacked.
- **Task 6 (fawley P4):** `make leak-check MODEL=fawley` → same, additionally proving markov is untouched (the S35 fawley→markov leak precedent).
- **Both landed together:** `make leak-check MODEL=markov,fawley`.

---

## 7. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **7.1** full-corpus harness can be a required PR gate within CI budget | ✅ VERIFIED (with a correction) | The full-corpus sweep **already runs** as a PR-triggered CI job inside a 25-min ceiling and is green on every triggering PR — so budget is not the constraint. **Correction:** it is *not* a *required* check (`contexts: []`) and no fast/nightly split is warranted (§4). The missing piece was the `--expect-drift` assertion, now implemented + verified (§3). |
| **1.3** the markov discriminator's full-corpus leak gate | ✅ VERIFIED (instrument ready) | `make leak-check MODEL=markov` is implemented and verified against 4 scenarios, including the exact S36 leak shape (C) and the laundering path that hid it (D). The instrument that catches cesam/ferts/sroute now exists; Task 4 supplies the discriminator it will gate. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 3 (leak-harness design + stand-up).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team
